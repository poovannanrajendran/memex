---
title: "Chunking"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-21
confidence: high
---

## Definition
The process of dividing large texts or documents into smaller, manageable segments ('chunks') to fit within the limited context window of most large language models for processing and retrieval.

## Why it matters (in Poovi's context)
The memex system explicitly avoids chunking due to the large context window of Gemini 2.5 Pro, addressing a common pain point in AI applications that can lead to fragmented understanding and retrieval hallucination.

## Key properties or components
- segmentation of text
- addresses context window limitations
- can fragment context
- can lead to retrieval issues

## Contradictions or debates
None.

## Sources
- [[building_memex_the_vision_and_tech_stack]]

## Related concepts
- [[context_window]]
- [[retrieval_hallucination]]
