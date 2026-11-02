"""Durable, idempotent local embedding and confirmed Qdrant delivery."""
import hashlib
import json
import math
import os
from pathlib import Path
import uuid
import requests


def validate_vector(vector, dimensions=768):
    if (not isinstance(vector, list) or len(vector) != dimensions or
            any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in vector) or
            not any(x != 0 for x in vector)):
        raise ValueError("Embedding must be finite, non-zero and match collection dimensions")
    return vector


def enqueue_page(db, run_id, slug, entry, category="sources"):
    path = Path(entry.get("file_path") or f"wiki/{category}/{slug}.md")
    if not path.is_file():
        raise FileNotFoundError(f"Generated wiki page missing: {path}")
    content = path.read_text(encoding="utf-8")
    digest = hashlib.sha256(content.encode()).hexdigest()
    payload = {"type": category, "slug": slug, "title": entry.get("title", slug),
               "summary": entry.get("summary", ""), "file_path": str(path),
               "text": content, "source": "memex", "content_hash": digest}
    with db.get_cursor() as cur:
        cur.execute("""INSERT INTO delivery_outbox(run_id, slug, content_hash, payload)
                       VALUES (%s, %s, %s, %s::jsonb)
                       ON CONFLICT(slug) DO UPDATE SET run_id=EXCLUDED.run_id,
                       content_hash=EXCLUDED.content_hash, payload=EXCLUDED.payload,
                       status='pending', attempts=0, last_error=NULL, next_attempt_at=NOW(),
                       delivered_at=NULL WHERE delivery_outbox.content_hash <> EXCLUDED.content_hash""",
                    (str(run_id) if run_id else None, category + ":" + slug, digest, json.dumps(payload)))


def enqueue_source(db, run_id, file_path):
    relative = os.path.relpath(file_path)
    aliases = [file_path, relative, "./" + relative, os.path.abspath(file_path)]
    with db.get_cursor() as cur:
        cur.execute("""SELECT wiki_slug FROM ingested_files
                       WHERE file_path = ANY(%s) AND status = 'completed'
                       ORDER BY ingested_at DESC LIMIT 1""", (aliases,))
        row = cur.fetchone()
    if not row or not row.get("wiki_slug"):
        raise ValueError(f"No recorded wiki_slug for completed source: {file_path}")
    slug = row["wiki_slug"]
    with open("wiki_index.json", encoding="utf-8") as stream:
        index = json.load(stream)
    entry = index.get("sources", {}).get(slug)
    if entry is None:
        raise ValueError(f"Recorded wiki_slug absent from source index: {slug}")
    enqueue_page(db, run_id, slug, entry)


def embed_text(text, session=requests):
    model = os.environ.get("MEMEX_EMBED_MODEL", "nomic-embed-text:latest")
    url = os.environ["MEMEX_EMBED_URL"].rstrip("/")
    token = os.environ["MEMEX_EMBED_TOKEN"]
    response = session.post(url + "/api/embed", json={"model": model, "input": text},
                            headers={"Authorization": "Bearer " + token}, timeout=90)
    response.raise_for_status()
    data = response.json()
    if data.get("model") != model:
        raise ValueError("Embedding model identity mismatch")
    return validate_vector(data["embeddings"][0], int(os.environ.get("MEMEX_EMBED_DIMENSIONS", "768")))


def deliver(payload, session=requests):
    model = os.environ.get("MEMEX_EMBED_MODEL", "nomic-embed-text:latest")
    dimensions = int(os.environ.get("MEMEX_EMBED_DIMENSIONS", "768"))
    text = "search_document: " + payload["title"] + "\n" + payload["text"][:6000]
    vector = embed_text(text, session)
    host = os.environ.get("QDRANT_HOST", "http://192.168.1.20:6333").rstrip("/")
    collection = os.environ.get("MEMEX_QDRANT_COLLECTION", "memex-knowledge-768d")
    headers = {"api-key": os.environ.get("QDRANT_API_KEY", "")}
    info = session.get(f"{host}/collections/{collection}", headers=headers, timeout=10)
    info.raise_for_status()
    config = info.json()["result"]["config"]["params"]["vectors"]
    if config.get("size") != dimensions:
        raise ValueError("Qdrant dimension mismatch")
    point_id = str(uuid.UUID(hashlib.sha256((payload["type"] + ":" + payload["slug"]).encode()).hexdigest()[:32]))
    point_payload = dict(payload, embedding_model=model, embedding_dimensions=dimensions,
                         embedding_input_chars=len(text), embedding_truncated=len(payload["text"]) > 6000)
    response = session.put(f"{host}/collections/{collection}/points?wait=true",
                           headers=headers, json={"points": [{"id": point_id, "vector": vector,
                                                               "payload": point_payload}]}, timeout=30)
    response.raise_for_status()
    body = response.json()
    if body.get("status") != "ok" or body.get("result", {}).get("status") != "completed":
        raise RuntimeError("Qdrant did not confirm completed write")
    return point_id


def drain_outbox(db, limit=20, sender=deliver):
    """Caller holds pipeline lock; failures remain pending with bounded backoff."""
    with db.get_cursor() as cur:
        cur.execute("""SELECT id, payload, attempts FROM delivery_outbox
                       WHERE status='pending' AND next_attempt_at <= NOW()
                       ORDER BY id LIMIT %s""", (limit,))
        rows = cur.fetchall()
    result = {"delivered": 0, "failed": 0}
    for row in rows:
        try:
            sender(row["payload"])
        except Exception as exc:
            with db.get_cursor() as cur:
                cur.execute("""UPDATE delivery_outbox SET attempts=attempts+1, last_error=%s,
                               next_attempt_at=NOW()+(%s * INTERVAL '1 second') WHERE id=%s""",
                            (str(exc)[:2000], min(3600, 60 * 2 ** min(row["attempts"], 6)), row["id"]))
            result["failed"] += 1
        else:
            with db.get_cursor() as cur:
                cur.execute("""UPDATE delivery_outbox SET status='delivered', attempts=attempts+1,
                               delivered_at=NOW(), last_error=NULL WHERE id=%s""", (row["id"],))
            result["delivered"] += 1
    with db.get_cursor() as cur:
        cur.execute("SELECT count(*) AS pending FROM delivery_outbox WHERE status='pending'")
        result["pending"] = cur.fetchone()["pending"]
    return result


def semantic_search(query, limit=5, session=requests):
    vector = embed_text("search_query: " + query, session)
    host = os.environ.get("QDRANT_HOST", "http://192.168.1.20:6333").rstrip("/")
    collection = os.environ.get("MEMEX_QDRANT_COLLECTION", "memex-knowledge-768d")
    response = session.post(f"{host}/collections/{collection}/points/search",
        headers={"api-key": os.environ.get("QDRANT_API_KEY", "")},
        json={"vector": vector, "limit": max(1, min(limit, 20)),
              "with_payload": ["title", "slug", "type", "summary", "file_path", "embedding_model"]},
        timeout=30)
    response.raise_for_status()
    return response.json()["result"]


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    from scripts.db import db
    from scripts.lock import pipeline_lock
    load_dotenv()
    parser = argparse.ArgumentParser(description="Queue and retry real local embeddings without Gemini calls")
    parser.add_argument("--enqueue-index", action="store_true")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.limit <= 10000:
        parser.error("--limit must be between 1 and 10000")
    with pipeline_lock():
        db.validate_schema()
        if args.enqueue_index:
            index = json.loads(Path("wiki_index.json").read_text())
            for category in ["sources", "entities", "concepts", "synthesis"]:
                for slug, entry in index.get(category, {}).items():
                    if slug:
                        enqueue_page(db, None, slug, entry, category)
        print(json.dumps(drain_outbox(db, limit=args.limit)))
