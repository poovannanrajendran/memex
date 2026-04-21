# memex — Poovi's AI-Maintained Second Brain

![memex Architecture](docs/images/architecture.png)

> "After 30 apps in 30 days — I realised I had a different problem. I was consuming more information than ever... and retaining almost none of it in a useful, connected form."

**memex** is more than a note-taking tool; it's a machine extension of human memory. Inspired by Vannevar Bush's 1945 vision, this project leverages the **1M-token context window** of the Google Gemini ecosystem to build a knowledge base that doesn't just *search*, but *reasons*.

---

## 🧠 The Vision: Moving Beyond RAG

Standard RAG (Retrieval-Augmented Generation) systems retrieve fragments of information. They don't reason across sources, they don't resolve contradictions, and they don't compound.

**memex** changes the architecture. Instead of a "searcher," the AI acts as a **Research Librarian**:
- **Ingesting**: Deep analysis of long-form sources in a single pass.
- **Cross-linking**: Automatically identifying connections between disparate ideas.
- **Synthesising**: Building a living, interlinked wiki where knowledge compounds over time.

---

## 🏛️ The Architecture: Three Layers

1.  **`raw/` — Immutable Source Inbox**
    The ground truth. Research papers, podcast transcripts, market articles, and YouTube records. Never modified.
2.  **`wiki/` — Agent-Maintained Knowledge**
    The living layer. Interlinked Markdown files for Entities, Concepts, and Synthesis pages. This is the "declarative memory" of the system.
3.  **`output/` — Deep Analysis**
    The result of the loop. Synthesis reports, health checks, and cross-domain reasoning.

---

## 🛠️ The Tech Stack: Powered by Google AI

![memex Tech Stack](docs/images/tech-stack.png)

The Gemini long-context window isn't a "nice-to-have" here—it's what makes this architecture possible. By loading full research papers or multi-document sets in a single pass, we eliminate chunking and retrieval hallucination.

- **Gemini CLI**: The agent runtime for the entire pipeline.
- **Gemini 2.5 Pro**: Used for deep synthesis and contradiction resolution.
- **Gemini 2.5 Flash**: Fast, cheap ingestion and daily wiki health checks.
- **Python 3.12**: The automation engine (`ingest.py`, `lint.py`, `synthesise.py`).
- **Obsidian**: The human-facing interface for visualising the knowledge graph.
- **Git**: The audit trail. Every edit made by the AI librarian is a commit.
- **Proxmox Homelab**: Local execution via **OpenClaw** for privacy and performance.

---

## 🚀 Getting Started

### **Usage**
- **Ingest**: Drop a source in `raw/` and run `python scripts/ingest.py raw/articles/`.
- **Synthesise**: Run `python scripts/synthesise.py "AI agent design patterns"`.
- **Audit**: Run `python scripts/lint.py` to keep the library tidy.

---

## 👤 About the Curator

**Poovannan Rajendran (Poovi)** is a rare hybrid: a Senior Account Manager at **Verisk** with 20+ years in the **Lloyd's of London** insurance market, combined with the technical capability to ship production AI systems. 

This memex serves as his primary research hub for Lloyd's market intelligence, AI engineering, and the **Mahabharata Moments** podcast.

---

## 📜 License

MIT © 2026 Poovannan Rajendran.
