# GEMINI.md — Second Brain Operating Manual

> This file is the persistent context for the Gemini CLI agent.
> Load it at the start of every session. It is the contract between you (the agent) and this vault.
> Do not modify this file during normal operation. Changes are made deliberately and committed via Git.

---

## Identity and purpose

This is **Poovi's Second Brain** — a personal knowledge base maintained by a Gemini CLI agent following the Karpathy LLM Wiki pattern.

**Owner:** Poovannan Rajendran (Poovi)  
**Domains:** Lloyd's and specialty insurance · AI engineering and agent systems · podcast production (Mahabharata Moments) · personal productivity  
**Agent runtime:** Gemini CLI (model: gemini-2.5-pro or gemini-2.5-flash as appropriate)  
**Obsidian vault path:** `~/second-brain/` (adjust to actual path on first run)

**Core principle:** The LLM is the librarian. Poovi is the curator.
Raw sources are immutable. The wiki is agent-maintained. Synthesis compounds over time.

---

## Vault structure

```
second-brain/
├── raw/                    # Immutable source inbox — never modify files here
│   ├── articles/           # Web clips, markdown articles
│   ├── pdfs/               # Papers, reports, documents
│   ├── transcripts/        # Meeting notes, podcast transcripts
│   ├── youtube/            # YouTube liked-video records (see spec below)
│   └── assets/             # Images and attachments
├── wiki/                   # Agent-maintained wiki — you own this layer
│   ├── sources/            # One summary page per ingested source
│   ├── entities/           # People, organisations, tools, products
│   ├── concepts/           # Ideas, frameworks, theories, patterns
│   ├── synthesis/          # Cross-source comparisons, analyses, themes
│   ├── index.md            # Master catalogue — always up to date
│   └── log.md              # Chronological record of all agent operations
└── output/                 # Reports, exports, generated artefacts
```

---

## Source types and ingestion rules

### Standard sources (articles, PDFs, transcripts)

Each file in `raw/` produces:
1. A summary page in `wiki/sources/` — filename matches source, snake_case
2. Updates to any relevant `wiki/entities/` pages
3. Updates to any relevant `wiki/concepts/` pages
4. A new entry in `wiki/log.md`
5. An updated entry in `wiki/index.md`

### YouTube liked-video records (`raw/youtube/`)

Each record is a JSON or markdown file containing:
- `url` — canonical YouTube URL
- `title` — video title
- `keywords` — comma-separated tags
- `transcript` — full or partial transcript
- `llm_summary` — pre-computed summary from the pipeline

**Ingestion rules for YouTube records:**

- Do NOT re-summarise if `llm_summary` is present — use it as the authoritative summary
- Extract named entities (people, tools, organisations) from title + keywords + summary
- Extract concepts and frameworks mentioned in the transcript or summary
- Create or update `wiki/entities/` pages for all named speakers or key figures
- Create or update `wiki/concepts/` pages for any distinct idea or framework
- Write a `wiki/sources/` page using the template below
- If the video is a lecture, talk, or interview: note the speaker as the primary entity and link their entity page
- Cross-link to any existing wiki pages whose topics are mentioned

---

## Page templates

### wiki/sources/[source-slug].md

```markdown
---
title: "[Source title]"
source_type: article | pdf | transcript | youtube
url: "[original URL if applicable]"
ingested: YYYY-MM-DD
confidence: high | medium | low
tags: []
---

## Summary
[2–4 sentence summary in plain prose. For YouTube: use llm_summary verbatim or lightly edited.]

## Key claims
- [Claim 1]
- [Claim 2]

## Entities mentioned
- [[Person or org name]]

## Concepts covered
- [[Concept name]]

## Contradictions or open questions
[Flag any claims that conflict with existing wiki pages. Leave blank if none.]

## Source
[Citation or link]
```

### wiki/entities/[entity-slug].md

```markdown
---
title: "[Entity name]"
entity_type: person | organisation | tool | product
tags: []
last_updated: YYYY-MM-DD
---

## Overview
[Who or what this is — 2–3 sentences.]

## Role in this knowledge base
[Why this entity appears — what domain, what relevance to Poovi's work.]

## Key facts
- [Fact]

## Sources
- [[source-slug]]

## Related concepts
- [[concept-slug]]
```

### wiki/concepts/[concept-slug].md

```markdown
---
title: "[Concept name]"
domain: insurance | ai-engineering | productivity | podcast | general
tags: []
last_updated: YYYY-MM-DD
confidence: high | medium | low
---

## Definition
[Clear, plain-English definition. 1–3 sentences.]

## Why it matters (in Poovi's context)
[Relevance to Lloyd's market, AI engineering, or personal projects.]

## Key properties or components
- [Property]

## Contradictions or debates
[If sources disagree on this concept, flag it here.]

## Sources
- [[source-slug]]

## Related concepts
- [[concept-slug]]
```

### wiki/synthesis/[synthesis-slug].md

```markdown
---
title: "[Synthesis title]"
synthesis_type: comparison | timeline | deep-dive | contradiction-resolution
sources: []
created: YYYY-MM-DD
---

## Thesis
[One sentence: what this synthesis establishes.]

## Analysis
[Prose. Cross-source reasoning. 3–8 paragraphs.]

## Conclusions
- [Conclusion 1]

## Open questions
- [Question]

## Sources used
- [[source-slug]]
```

---

## Slash commands

These are the four operations you respond to. Always confirm the operation and log it in `wiki/log.md`.

### /second-brain-ingest [file or folder]

**Purpose:** Process one or more raw source files into wiki pages.

**Steps:**
1. Read the source file(s). For YouTube records, load `url`, `title`, `keywords`, `transcript`, `llm_summary`.
2. Identify all entities and concepts referenced.
3. Check `wiki/index.md` for existing pages that should be updated.
4. Write or update `wiki/sources/`, `wiki/entities/`, and `wiki/concepts/` pages.
5. Flag any contradictions with existing pages inline in the relevant page under "Contradictions".
6. Update `wiki/index.md` and append to `wiki/log.md`.
7. Commit: `git add wiki/ && git commit -m "ingest: [source title or slug]"`

**Model choice:** Use `gemini-2.5-pro` for long transcripts or PDFs (>10,000 words). Use `gemini-2.5-flash` for short articles and YouTube summaries.

### /second-brain-query [question]

**Purpose:** Answer a question using wiki content as the primary source.

**Steps:**
1. Search `wiki/index.md` for relevant pages by topic.
2. Load the relevant pages as context.
3. Answer the question with citations to specific wiki pages using `[[wikilink]]` format.
4. If the answer requires synthesis across multiple pages, say so explicitly.
5. If the answer is not in the wiki, say so — do not hallucinate. Suggest which raw sources might contain the answer.

**Do not modify wiki pages during a query.**

### /second-brain-lint

**Purpose:** Health-check the wiki for structural issues.

**Checks to run:**
1. Broken wikilinks — scan all `[[...]]` references and verify the target file exists
2. Orphan pages — pages in `wiki/` with no inbound links
3. Stale pages — sources pages with `ingested` date older than 180 days (flag, do not delete)
4. Missing index entries — pages in `wiki/` not listed in `wiki/index.md`
5. Empty contradiction sections — not an error, just skip
6. Pages missing required frontmatter fields

**Output:** A lint report in `output/lint-[YYYY-MM-DD].md`. List issues by category. Offer to fix broken wikilinks and missing index entries automatically. Never auto-delete.

### /second-brain-synthesise [topic or question]

**Purpose:** Produce a cross-source synthesis page on a specific topic.

**Steps:**
1. Query the index for all pages related to the topic.
2. Load relevant `wiki/sources/`, `wiki/entities/`, and `wiki/concepts/` pages.
3. Identify patterns, agreements, contradictions, and open questions across sources.
4. Write a new `wiki/synthesis/[slug].md` using the synthesis template.
5. Add backlinks from all referenced concept and source pages to the new synthesis page.
6. Update `wiki/index.md` and `wiki/log.md`.
7. Commit: `git add wiki/ && git commit -m "synthesis: [topic]"`

---

## Writing conventions

- **Language:** British English throughout (organise, analyse, recognise, programme)
- **Tone:** Clear, precise, professional — not conversational, not academic
- **Wikilinks:** Use `[[page-title]]` format for all internal references. Never use bare URLs for internal links.
- **Frontmatter:** Always include. Use ISO dates (YYYY-MM-DD).
- **Confidence scoring:** Apply `high` when multiple independent sources agree. Apply `medium` for single-source claims. Apply `low` for inferred or synthesised conclusions.
- **Never modify `raw/`** — it is the immutable source of truth
- **Always commit after writing** — every wiki change is a Git commit

---

## Gemini-specific behaviours

- **Long context:** For sources exceeding 50,000 tokens, load the full file directly — do not chunk. Use `gemini-2.5-pro` with its 1M token context window.
- **Structured output:** When extracting entities and concepts from a source, produce a structured JSON summary internally before writing wiki pages. This keeps writes deterministic.
- **Search grounding:** When running `/second-brain-lint` and checking staleness, you may use Gemini's built-in Search grounding tool to verify whether key claims on a flagged page have been superseded by more recent information.
- **Model routing:**
  - `gemini-2.5-pro` → ingest of long documents, synthesis, contradiction resolution
  - `gemini-2.5-flash` → lint, short article ingest, query answering, index updates

---

## Log format (wiki/log.md)

Append one entry per operation. Never rewrite existing entries.

```
## YYYY-MM-DD HH:MM

**Operation:** ingest | query | lint | synthesise  
**Input:** [file, question, or topic]  
**Output:** [pages written or updated, lint issues found, synthesis created]  
**Notes:** [anything unusual]
```

---

## Index format (wiki/index.md)

Three sections, alphabetical within each:

```markdown
# Second Brain Index

_Last updated: YYYY-MM-DD_

## Sources
- [[source-slug]] — [one-line description]

## Entities
- [[entity-slug]] — [one-line description]

## Concepts
- [[concept-slug]] — [one-line description]

## Synthesis
- [[synthesis-slug]] — [one-line description]
```

---

## OpenClaw Integration

Memex is connected to **OpenClaw** (Poovi's self-hosted AI agent gateway on `ai-node-01`).
This section defines how Gemini CLI interacts with the integration.

### What this means for wiki maintenance

1. **`raw/openclaw/`** is a valid source directory. Files dropped here by OpenClaw agents  
   follow the same ingest rules as `raw/articles/`. Source type: `transcript`.  
   Always tag them with `openclaw` and `agent-research` in frontmatter.

2. **After every watcher run**, a notification is sent to n8n which syncs new wiki pages  
   to Qdrant on `docker-host-01`. This is automatic — no action required.

3. **`wiki_index.json`** is read by OpenClaw agents for live search. It is rebuilt on  
   every `npm run build`. After bulk wiki changes (100+ pages), rebuild the index:  
   ```bash
   node quartz/bootstrap-cli.mjs build
   ```

4. **Synthesis docs** are highest-priority for OpenClaw agents. When creating a new  
   synthesis, also update `wiki_index.json` by rebuilding. The synthesis content is  
   injected into agent context with higher weight than source/entity/concept pages.

### New slash command: /second-brain-openclaw-push [topic]

**Purpose:** Research a topic and write a new source file to `raw/openclaw/` for Memex ingestion.  
This is used when an OpenClaw agent (typically `market-intel`) asks Memex to absorb new research.

**Steps:**
1. Research the topic using available knowledge and sources.
2. Format the research as a Memex source page (use the `wiki/sources/` template).
3. Set frontmatter: `source_type: transcript`, `tags: [openclaw, agent-research]`, `agent_id: <caller>`.
4. Write to `raw/openclaw/[slug].md`.
5. POST to runner_api `/ingest` with `path: raw/openclaw/[slug].md`, `trigger_source: openclaw`.
6. Confirm with `run_id` from response.
7. Log in `wiki/log.md`:  
   `**Operation:** openclaw-push | **Input:** [topic] | **Output:** [slug].md created`

**Never write sensitive data** (API keys, passwords, personal contact details) to `raw/openclaw/`.

### Write-back file format

All files written to `raw/openclaw/` must use this template:

```markdown
---
title: "[Title of the research]"
source_type: transcript
url: ""
ingested: YYYY-MM-DD
confidence: medium
tags: [openclaw, agent-research, <agent_id>]
agent_id: <openclaw-agent-id>
trigger_source: openclaw
---

## Summary
[2-4 sentence summary]

## Key claims
- [Claim]

## Entities mentioned
- [[Entity]]

## Concepts covered
- [[Concept]]

## Contradictions or open questions
[Conflicts with existing Memex knowledge, if any]

## Source
Agent research — {agent_id} — {YYYY-MM-DD}
```

### runner_api endpoints (available on localhost:8000)

| Endpoint | Method | Auth | Description |
|---------|--------|------|-------------|
| `/search` | GET | Bearer | Search wiki_index.json — params: `q`, `type`, `limit` |
| `/wiki/{type}/{slug}` | GET | Bearer | Fetch full wiki entry + markdown |
| `/wiki/synthesis/list` | GET | Bearer | List all synthesis docs |
| `/ingest` | POST | Bearer | Trigger ingest — accepts `content` + `filename` for write-back |
| `/run` | POST | Bearer | Trigger full watcher pipeline |
| `/status` | GET | Bearer | Last 5 pipeline runs |

---

## OpenClaw Integration

Memex is connected to **OpenClaw** (Poovi's self-hosted AI agent gateway on `ai-node-01`).
This section defines how Gemini CLI interacts with the integration.

### What this means for wiki maintenance

1. **`raw/openclaw/`** is a valid source directory. Files dropped here by OpenClaw agents  
   follow the same ingest rules as `raw/articles/`. Source type: `transcript`.  
   Always tag them with `openclaw` and `agent-research` in frontmatter.

2. **After every watcher run**, a notification is sent to n8n which syncs new wiki pages  
   to Qdrant on `docker-host-01`. This is automatic — no action required.

3. **`wiki_index.json`** is read by OpenClaw agents for live search. It is rebuilt on  
   every `npm run build`. After bulk wiki changes (100+ pages), rebuild the index:  
   ```bash
   node quartz/bootstrap-cli.mjs build
   ```

4. **Synthesis docs** are highest-priority for OpenClaw agents. When creating a new  
   synthesis, also update `wiki_index.json` by rebuilding. The synthesis content is  
   injected into agent context with higher weight than source/entity/concept pages.

### New slash command: /second-brain-openclaw-push [topic]

**Purpose:** Research a topic and write a new source file to `raw/openclaw/` for Memex ingestion.  
This is used when an OpenClaw agent (typically `market-intel`) asks Memex to absorb new research.

**Steps:**
1. Research the topic using available knowledge and sources.
2. Format the research as a Memex source page (use the `wiki/sources/` template).
3. Set frontmatter: `source_type: transcript`, `tags: [openclaw, agent-research]`, `agent_id: <caller>`.
4. Write to `raw/openclaw/[slug].md`.
5. POST to runner_api `/ingest` with `path: raw/openclaw/[slug].md`, `trigger_source: openclaw`.
6. Confirm with `run_id` from response.
7. Log in `wiki/log.md`:  
   `**Operation:** openclaw-push | **Input:** [topic] | **Output:** [slug].md created`

**Never write sensitive data** (API keys, passwords, personal contact details) to `raw/openclaw/`.

### Write-back file format

All files written to `raw/openclaw/` must use this template:

```markdown
---
title: "[Title of the research]"
source_type: transcript
url: ""
ingested: YYYY-MM-DD
confidence: medium
tags: [openclaw, agent-research, <agent_id>]
agent_id: <openclaw-agent-id>
trigger_source: openclaw
---

## Summary
[2-4 sentence summary]

## Key claims
- [Claim]

## Entities mentioned
- [[Entity]]

## Concepts covered
- [[Concept]]

## Contradictions or open questions
[Conflicts with existing Memex knowledge, if any]

## Source
Agent research — {agent_id} — {YYYY-MM-DD}
```

### runner_api endpoints (available on localhost:8000)

| Endpoint | Method | Auth | Description |
|---------|--------|------|-------------|
| `/search` | GET | Bearer | Search wiki_index.json — params: `q`, `type`, `limit` |
| `/wiki/{type}/{slug}` | GET | Bearer | Fetch full wiki entry + markdown |
| `/wiki/synthesis/list` | GET | Bearer | List all synthesis docs |
| `/ingest` | POST | Bearer | Trigger ingest — accepts `content` + `filename` for write-back |
| `/run` | POST | Bearer | Trigger full watcher pipeline |
| `/status` | GET | Bearer | Last 5 pipeline runs |
| `/linkedin/post` | POST | Bearer | Post to Poovi's LinkedIn profile |

## What to never do

- Modify any file in `raw/` — it is read-only
- Delete wiki pages — mark as deprecated in frontmatter instead
- Answer queries with content not traceable to the wiki or raw sources
- Use heading-level numbers (H1 through H3 only)
- Create pages without frontmatter
- Commit without a meaningful message
