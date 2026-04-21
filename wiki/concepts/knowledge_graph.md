---
title: "Knowledge Graph"
domain: ai-engineering
tags: [data-structures, ai, search]
last_updated: 2026-04-20
confidence: high
---

## Definition
A knowledge graph is a programmatic way to represent a network of real-world entities and their interrelations. It uses nodes (entities) and edges (relationships) to store data in a way that is easily queryable by both humans and machines.

## Why it matters (in Poovi's context)
Fundamental to the [[memex]] project and tools like [[graphify]]. It allows for "declarative memory" that an AI agent can query without loading every raw source file into context.

## Key properties or components
- **Nodes:** Represent entities (e.g., people, tools, concepts).
- **Edges:** Represent relationships (e.g., "mentions", "implements", "works-on").
- **Provenance:** Tracking the origin of a fact (e.g., [[graphify]]'s EXTRACTED vs INFERRED tags).

## Sources
- [[graphify_token_saving]]

## Related concepts
- [[llm_wiki_pattern]]
- [[token_efficiency]]
