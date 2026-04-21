# memex — PRD v1 (Original MVP)

## 1. Product Summary
**memex** v1 is an agent-maintained knowledge base built on the **LLM Wiki Pattern**. It aims to automate the conversion of raw source materials (articles, transcripts) into a structured graph of entities and concepts.

## 2. Target Users
- Individual researchers and builders needing to maintain high-context across disparate domains.
- Domain experts (e.g., Lloyd's insurance) managing massive volumes of news and reports.

## 3. Core Requirements (v1)

### 3.1 Immutable Source Handling
- Support for Markdown, TXT, and HTML files in a `raw/` directory.
- Support for YouTube "Liked Video" records (URL + Metadata + Summary).
- **Rule**: Never modify files in the `raw/` directory.

### 3.2 Ingestion Engine (The Librarian)
- Extract named entities (People, Organisations, Tools).
- Extract key concepts and frameworks.
- Generate a summary page for every source using a standardised Markdown template.
- Support for **British English** (organise, analyse).

### 3.3 Wiki Structure
- One file per entity in `wiki/entities/`.
- One file per concept in `wiki/concepts/`.
- Automatic interlinking using `[[wikilinks]]`.
- A master `index.md` and a chronological `log.md`.

### 3.4 Command Interface
- Operation via Gemini CLI slash commands:
  - `/second-brain-ingest [path]`
  - `/second-brain-query [question]`
  - `/second-brain-lint`

## 4. Technical Constraints
- No cloud storage (local-first).
- Markdown as the primary data format.
- Git for version control and audit trail.

## 5. Success Metrics
- 100% resolution of wikilinks (no broken links).
- Successful extraction of at least 5 entities per technical article.
- Validated "one commit per ingest" Git history.
