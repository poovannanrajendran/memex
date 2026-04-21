---
title: "Context window"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-21
confidence: high
---

## Definition
The maximum amount of text (measured in tokens) that a large language model can process and understand in a single input or interaction, influencing its ability to grasp broader context.

## Why it matters (in Poovi's context)
A critical technical specification for memex, as Gemini 2.5 Pro's 1M+ token context window fundamentally changes the system's architecture by enabling one-shot analysis of entire long documents and eliminating the need for chunking.

## Key properties or components
- measured in tokens
- determines input capacity
- impacts model's ability to retain long-range dependencies
- influences system architecture

## Contradictions or debates
None.

## Sources
- [[building_memex_the_vision_and_tech_stack]]

## Related concepts
- [[gemini_2_5_pro]]
- [[chunking]]
- [[retrieval_hallucination]]
