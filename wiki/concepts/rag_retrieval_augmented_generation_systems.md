---
title: "RAG (Retrieval Augmented Generation) systems"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-21
confidence: high
---

## Definition
An architectural pattern for large language models where the model first retrieves relevant documents or data from an external knowledge base. This retrieved information is then used to augment the prompt, helping the LLM generate more accurate and contextually relevant responses.

## Why it matters (in Poovi's context)
The author contrasts RAG systems with their memex project, highlighting RAG's limitations (only retrieval, no reasoning, contradiction resolution, or compounding) to underscore the advanced, librarian-like capabilities intended for memex.

## Key properties or components
- retrieves information
- augments LLM prompt
- generates response
- reduces hallucination (compared to pure LLM)
- typically does not reason across sources
- typically does not resolve contradictions

## Contradictions or debates
The source implies that traditional RAG systems are limited because they "don't reason across sources. They don't resolve contradictions. They don't compound." This serves as a key differentiator for the memex project.

## Sources
- [[building_memex_the_vision_and_tech_stack]]

## Related concepts
- [[large_language_models]]
- [[hallucination]]
- [[context_window]]
