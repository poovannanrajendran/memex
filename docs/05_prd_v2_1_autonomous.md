# memex — PRD v2.1 (Autonomous Intelligence Infrastructure)

## 1. Product Summary
**memex** v2.1 transitions from a local polling system to a fully autonomous, server-side intelligence engine. It introduces cross-server database watching, robust error handling for real-world web data, and automated Git synchronization across the homelab infrastructure.

## 2. Technical Delta (v2.1 vs v2.0)

| Feature | v2.0 (Optimised) | v2.1 (Autonomous) |
| :--- | :--- | :--- |
| **Infrastructure** | Local Machine (MacBook) | **Remote Runner** (`automation-runner-01`). |
| **Data Source** | Local Filesystem (`raw/`) | **External PostgreSQL** (`youtube_liked_videos`). |
| **Ingestion** | Single-source | **Hybrid Fallback**: Transcripts -> Descriptions. |
| **Resilience** | Basic character cleaning | **YAML Escaping**: Automatic double-quote handling. |
| **Synchronization** | Manual push | **Automated Sync**: Headless `git push` to GitHub. |
| **Indexing** | Standalone JSON | **Markdown Reconstruction**: Auto-syncing `index.md`. |

## 3. New Requirements (v2.1)

### 3.1 Remote Watcher Strategy
- Monitor external PostgreSQL databases (`192.168.1.20`) from a dedicated automation node (`192.168.1.30`).
- Process delta records every hour at `:18` to ensure near-real-time knowledge availability.
- Dynamic environment detection using `sys.executable` for cross-platform Python execution.

### 3.2 Enhanced Knowledge Extraction
- **Content Recovery**: Use high-quality video descriptions as a fallback when transcripts are unavailable.
- **Usability Filtering**: Advanced regex filtering to skip low-signal descriptions (hashtags, links only).
- **Relative Stubbing**: Automated creation of stub pages for `related_concepts` to ensure a 100% interconnected graph.

### 3.3 Zero-Maintenance Indexing
- Automatic reconstruction of `wiki/index.md` from `wiki_index.json`.
- Categorized view of all 5,500+ pages (Sources, Entities, Concepts, Synthesis).

## 4. Current Infrastructure Flow

1.  **Detect**: `youtube_watcher.py` queries remote PG for `isprocessed=false`.
2.  **Filter**: Identifies "Usable Content" (Transcript > 50 chars or Description > 150 chars).
3.  **Process**: `ingest.py` calls **Gemini 2.5 Flash Lite** for structured JSON output.
4.  **Escape**: Ingest script cleans titles to prevent Quartz build failures.
5.  **Expand**: Creates stubs for all new concepts to prevent broken links.
6.  **Update**: Indexer and Rebuilder refresh the global wiki navigation.
7.  **Sync**: Local commit + automated push to GitHub.

## 5. Achievement Metrics
- **Throughput**: Processed **770+ videos** in a single bulk run.
- **Accuracy**: 0 broken wikilinks across 5,500+ pages.
- **Cost Efficiency**: Total ingestion cost **<$0.50 USD** for years of video history.
