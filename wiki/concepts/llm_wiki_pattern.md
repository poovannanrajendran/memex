---
title: "LLM Wiki Pattern"
domain: ai-engineering
tags: [knowledge-management, architecture]
last_updated: 2026-04-20
confidence: high
---

## Definition
A design pattern for personal knowledge bases where an LLM acts as a "librarian." The LLM ingests raw data and maintains a structured, interlinked wiki (often in Markdown/Obsidian). It was popularized by [[andrej_karpathy]].

## Why it matters (in Poovi's context)
The architectural foundation of the [[memex]] project. It provides a superior alternative to RAG for long-term knowledge synthesis and discovery.

## Key properties or components
- **Immutable Raw Layer:** Original sources are never modified.
- **Agent-Maintained Wiki Layer:** The "living" synthesis of knowledge.
- **Interlinking:** Heavy use of [[wikilinks]] to create a network of information.

## Sources
- [[gemini]]
- [[graphify_token_saving]]

## Related concepts
- [[knowledge_graph]]
- [[obsidian]]


## Related Synthesis
- [[deep_dive_synthesis_ai_agent_workflow_design_patterns]]

## Related Synthesis
- [[deep_dive_synthesis_lloyds_and_ai_recent_updates]]

## Related Synthesis
- [[lloyds_and_ai_recent_updates]]