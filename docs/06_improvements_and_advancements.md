# memex — Technical Improvements & Advancements

This document tracks the specific "quality of life" and infrastructure tweaks implemented to ensure the stability and scalability of the memex.

## 1. Quartz Site Stability Fixes
- **Clean URL Support**: Migrated `vercel.json` to use `cleanUrls: true` and `trailingSlash: false`. This ensures that pages like `/concepts/ai_agent` work perfectly without the `.html` extension.
- **Asset Resolution**: Added explicit rewrites for `index.css`, `prescript.js`, and `postscript.js` to fix broken styling on subpages.
- **Missing Emitters**: Restored the `ComponentResources` emitter in `quartz.config.ts` to ensure core CSS/JS assets are generated during every build.
- **Casing Consistency**: Standardised sensitive files (e.g., `README.md` to `readme.md`) and added mandatory frontmatter to ensure they are captured by the Quartz generator.

## 2. Robust Ingestion Logic
- **YAML Safety**: Implemented automatic escaping of double quotes in all generated Markdown titles. This prevents common build failures caused by YouTube video titles containing quotes or complex emojis.
- **Intelligence Fallbacks**: 
    - Added a tiered extraction strategy: If a transcript is unavailable, the system automatically falls back to the video **Description**.
    - Implemented a "Usability Filter" that checks the signal-to-noise ratio of descriptions (ignoring hashtags and links) to ensure the wiki stays high-quality.
- **Link Integrity**: The ingestion script now pre-emptively creates stub pages for all `related_concepts` found by the LLM. This ensures that the Obsidian graph is always 100% interconnected with zero broken links.

## 3. Autonomous Server-Side Operations
- **Headless Environment**: Configured a standalone virtual environment (`venv`) on `automation-runner-01` to manage all dependencies in isolation from the system Python.
- **Dynamic Execution**: Updated all subprocess calls to use `sys.executable`, making scripts portable between MacBook (MacOS) and Linux Runner (Ubuntu) environments.
- **Auto-Sync Pipeline**: 
    - Integrated `git commit` and `git push` directly into the watcher pipeline.
    - Handled the "unrelated histories" merge between local and server Git repositories to enable a unified GitHub timeline.
- **Automated Rebuilding**: Integrated `indexer.py` and `rebuild_index_md.py` into the ingestion flow, ensuring the site index is always up-to-date without human intervention.

## 4. Maintenance & Operations
- **Log Management**: All automated runs append to `wiki/log.md`, providing a permanent, human-readable audit trail of every video processed.
- **Cron Scheduling**: Standardised on an hourly `:18` trigger to avoid peak-hour congestion and ensure consistent updates.
