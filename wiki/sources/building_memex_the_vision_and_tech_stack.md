---
title: "Building memex — The Vision and Tech Stack"
source_type: article
url: ""
ingested: 2026-11-02
confidence: medium
tags: ["knowledge management", "second brain", "AI", "Vannevar Bush", "Gemini"]
---

## Summary
This LinkedIn post details the vision and technical architecture behind Memex, an AI-powered knowledge management system. The author, facing information overload, sought to build a "machine extension of human memory" inspired by Vannevar Bush's concept. Unlike traditional tools that merely organise or retrieve information, Memex aims to ingest, link, synthesise, and resolve contradictions across vast amounts of data, acting more like a human research librarian.

## Key claims
- Traditional knowledge management tools fail to address the core problem of information overload and disconnected knowledge.
- The "memex" concept, originally proposed by Vannevar Bush, provides a foundational vision for a true "second brain".
- Modern AI, particularly large context window models like Gemini 2.5 Pro, makes building a functional memex a reality.
- Memex aims to ingest, cross-link, synthesise, and resolve contradictions in information, rather than just retrieving it.
- The tech stack leverages Google's Gemini models for their large context windows, Python for automation, Obsidian for the user interface, and a local homelab for agent execution.

## Entities mentioned
- [[vannevar_bush]] — Conceptual inspiration for the "memex" project.
- [[google]] — Provider of the AI models (Gemini) and ecosystem powering Memex.
- [[gemini_2_5_pro]] — Core component for long-document ingestion, synthesis, and contradiction resolution within Memex.
- [[gemini_2_5_flash]] — Used for ingesting shorter articles and performing routine health checks within Memex.
- [[python_3_12]] — The programming language used for automation scripts (ingest, lint, synthesise) within the Memex tech stack.
- [[obsidian]] — The human-facing interface for the Memex system, where users interact with their connected knowledge.
- [[git]] — Provides an audit trail for the knowledge and changes within Memex.
- [[proxmox_homelab]] — Hosts the local AI agent (via OpenClaw) for Memex, providing a private and controlled environment.
- [[openclaw]] — Facilitates the execution of the AI agent on the Proxmox homelab.

## Concepts covered
- [[memex]] — Serves as the core concept and goal for the AI-maintained second brain being built, aiming to realise Bush's vision with modern technology.
- [[second_brain]] — The project aims to build an AI-maintained "second brain" that goes beyond simple storage to active reasoning and synthesis.
- [[retrieval_augmented_generation_rag]] — The author critiques standard RAG systems for merely retrieving information, distinguishing Memex's goal of reasoning and synthesis across sources.
- [[context_window]] — A large context window (like Gemini 2.5 Pro's 1M+ tokens) is critical for Memex, enabling the AI to ingest and reason over entire documents or multiple sources simultaneously without needing to break them into smaller chunks.

## Contradictions or open questions
None identified.

## Source
memex_vision_linkedin.md
