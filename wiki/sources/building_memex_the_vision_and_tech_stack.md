---
title: "Building memex — The Vision and Tech Stack"
source_type: article
url: ""
ingested: 2026-04-21
confidence: high
tags: ["Knowledge Management", "AI", "Second Brain", "LLM", "Tech Stack", "Automation", "Productivity", "Gemini"]
---

## Summary
The author began building 'memex', an AI-maintained second brain, after realising traditional knowledge tools failed to help retain and connect information from various sources like research papers, podcasts, and articles. Inspired by Vannevar Bush's original concept, this new system aims to go beyond simple retrieval by ingesting, cross-linking, and synthesising knowledge using advanced AI. The core technology leverages Google's Gemini 2.5 Pro and Flash models for their extensive context windows, enabling one-shot analysis and contradiction resolution, with Obsidian serving as the human interface.

## Key claims
- Traditional knowledge tools, often resembling 'better folders', are inadequate for truly retaining and connecting information from diverse sources.
- The memex project aims to build an AI-maintained 'second brain' that ingests, cross-links, and synthesises knowledge, mimicking a research librarian's function.
- Vannevar Bush's 1945 concept of 'memex' is now achievable with modern AI, specifically leveraging large language models with extensive context windows (e.g., 1M+ tokens).
- Standard RAG systems are limited as they retrieve but don't reason across sources, resolve contradictions, or compound knowledge.
- Google's Gemini 2.5 Pro's 1M+ token context window is crucial for memex, enabling one-shot analysis of long documents and eliminating the need for chunking and associated retrieval hallucination.
- The memex tech stack includes Gemini CLI, Gemini 2.5 Pro, Gemini 2.5 Flash, Python 3.12 for automation, Obsidian for the human interface, Git for audit trails, and a Proxmox homelab with OpenClaw for local agent hosting.

## Entities mentioned
- [[memex]] — The central product and project being built by the author, inspired by Vannevar Bush's original vision, to create an advanced knowledge management system.
- [[vannevar_bush]] — His coinage of the term 'memex' and his vision for a personal knowledge device directly inspired the author's project.
- [[google]] — The provider of the core AI models (Gemini series) and ecosystem chosen for the memex project, primarily due to their large context window capabilities essential for knowledge synthesis.
- [[gemini_2_5_pro]] — Serves as the backbone for complex AI operations within memex, handling long-document ingestion, deep synthesis, and crucial contradiction resolution across sources.
- [[gemini_2_5_flash]] — Used within memex for more efficient processing of shorter content, specifically for short article ingestion and performing 'wiki health checks' to ensure data quality.
- [[python_3_12]] — The programming language used to develop key automation scripts (ingest.py, lint.py, synthesise.py) that manage and process information within the memex system.
- [[obsidian]] — Functions as the human-facing interface for the memex system, providing the primary point of interaction for users to view, organise, and manage their AI-maintained knowledge.
- [[git]] — Used to maintain an audit trail for the memex system, ensuring that all changes and versions of the knowledge base are tracked and auditable.
- [[proxmox_homelab]] — Provides the local hosting environment for the memex system's AI agent, allowing it to run locally via OpenClaw.
- [[openclaw]] — Facilitates the operation of the local AI agent within the Proxmox homelab environment as part of the memex architecture.

## Concepts covered
- [[second_brain]] — This concept is the fundamental goal and inspiration behind the memex project, aiming to overcome the limitations of natural memory and traditional note-taking for knowledge workers.
- [[knowledge_problem]] — This is the core issue that the memex project seeks to solve, highlighting the inadequacies of existing tools and methods for modern information consumption.
- [[rag_systems]] — The source identifies RAG systems as a common limitation in standard knowledge tools because they primarily retrieve rather than reason across sources, resolve contradictions, or compound knowledge, thus motivating the development of memex's more advanced capabilities.
- [[context_window]] — A critical technical specification for memex, as Gemini 2.5 Pro's 1M+ token context window fundamentally changes the system's architecture by enabling one-shot analysis of entire long documents and eliminating the need for chunking.
- [[chunking]] — The memex system explicitly avoids chunking due to the large context window of Gemini 2.5 Pro, addressing a common pain point in AI applications that can lead to fragmented understanding and retrieval hallucination.
- [[retrieval_hallucination]] — The memex project aims to prevent this issue by leveraging large context windows that remove the need for chunking, thereby ensuring more coherent and accurate knowledge processing.
- [[ai_agent]] — In the memex system, the AI agent is envisioned as the 'librarian' responsible for the active ingestion, cross-linking, and synthesis of knowledge, making the system 'AI-maintained' and intelligent.
- [[research_librarian]] — This role serves as the ideal metaphor and operational model for how the memex system is designed to function, moving beyond simple search to active intellectual work on behalf of the user.
- [[synthesis]] — Synthesis is a core, differentiating capability of the memex system, allowing it to actively cross-link and consolidate knowledge from diverse sources, which is a limitation of simpler retrieval tools.
- [[contradiction_resolution]] — This is a key advanced capability of Gemini 2.5 Pro within memex, distinguishing it from standard RAG systems and ensuring the integrity and reliability of the knowledge base by actively addressing inconsistencies.
- [[knowledge_compounding]] — This is a desired outcome of the memex system, addressing a significant limitation of traditional tools that fail to allow knowledge to naturally 'compound' and generate new value.

## Contradictions or open questions
None identified.

## Source
memex_vision_linkedin.md
