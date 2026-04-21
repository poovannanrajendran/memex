---
title: "Building memex — The Vision and Tech Stack"
source_type: article
url: ""
ingested: 2026-04-21
confidence: high
tags: ["AI", "Knowledge Management", "Second Brain", "LLM", "Google", "Gemini", "Productivity", "Obsidian", "Vannevar Bush", "Automation", "Self-hosting", "AI Agent", "Context Window"]
---

## Summary
The author addresses a personal challenge of information overload and poor retention by developing "memex," an AI-maintained second brain. This project aims to move beyond simple information retrieval, instead focusing on deep synthesis, cross-linking, and contradiction resolution across diverse sources. By leveraging Google's Gemini models with their 1M+ token context windows, the author believes the 1945 vision of Vannevar Bush's memex, as a machine extension of human memory, can finally be realised.

## Key claims
- The author experienced a significant personal challenge of consuming vast amounts of information but retaining little in a useful, connected form.
- Most existing knowledge tools are limited to better folders or basic RAG retrieval, failing to reason across sources, resolve contradictions, or compound knowledge.
- The author's 'memex' project is an AI-maintained second brain designed to function more like a research librarian, ingesting, cross-linking, and synthesising information.
- Modern AI with large context windows, specifically Google's Gemini 2.5 Pro (1M+ tokens), makes the 1945 vision of Vannevar Bush's memex achievable, allowing for one-shot analysis without chunking or retrieval hallucination.
- Google's ecosystem is chosen for the memex project primarily due to the large context window capabilities of its Gemini models, which are crucial for synthesis across multiple documents.

## Entities mentioned
- [[vannevar_bush]] — Coined the concept of "memex," a hypothetical device for personal knowledge management, which serves as the foundational inspiration for the author's project.
- [[google]] — Its Gemini AI ecosystem provides the core large language models (Gemini 2.5 Pro, Gemini 2.5 Flash) and runtime (Gemini CLI) for the memex project, chosen for their extensive context windows.
- [[memex_project]] — The central project described in the source, addressing personal knowledge management challenges by leveraging AI for advanced synthesis and analysis.
- [[gemini_cli]] — Serves as the primary agent runtime for the memex project, facilitating interaction with Google's AI models.
- [[gemini_2_5_pro]] — Employed for critical functions within the memex project, including long-document ingestion, synthesis, and contradiction resolution, due to its ability to handle vast amounts of information.
- [[gemini_2_5_flash]] — Used for specific, lighter tasks within the memex system, such as short article ingestion and performing 'wiki health checks'.
- [[python_3_12]] — Provides the programming backbone for automation scripts (e.g., ingest.py, lint.py, synthesise.py) that manage and process information within the memex project.
- [[obsidian]] — Functions as the human-facing interface for the memex project, providing a user-friendly environment for interacting with the AI-maintained knowledge base.
- [[git]] — Maintains an audit trail for the memex project, likely tracking changes to the knowledge base or the codebase itself, ensuring version control and accountability.
- [[proxmox_homelab]] — Hosts the local agent via OpenClaw for the memex project, indicating a preference for self-hosting and local control over certain AI components.
- [[openclaw]] — Serves as the local agent for the memex system, running on the Proxmox homelab.

## Concepts covered
- [[memex_concept]] — It is the foundational vision inspiring the author's project, aiming to achieve Bush's concept of a personal knowledge machine using modern AI capabilities.
- [[second_brain]] — The memex project is explicitly described as an 'AI-maintained second brain,' highlighting its core purpose to augment human memory and intelligence by externalising and synthesising knowledge.
- [[ai_agent]] — The memex project positions an AI agent as the 'librarian' responsible for ingesting, cross-linking, and synthesising information, making it central to achieving the project's vision of an advanced knowledge system.
- [[knowledge_management]] — The entire memex project stems from the author's personal 'classic knowledge problem,' aiming to overcome the limitations of scattered notes and unconnected ideas through a structured, AI-driven knowledge system.
- [[rag_retrieval_augmented_generation_systems]] — The author contrasts RAG systems with their memex project, highlighting RAG's limitations (only retrieval, no reasoning, contradiction resolution, or compounding) to underscore the advanced, librarian-like capabilities intended for memex.
- [[context_window]] — A large context window (e.g., 1M+ tokens in Gemini 2.5 Pro) is identified as fundamental for the memex project, enabling 'one-shot analysis' of long documents without chunking and entirely changing the system architecture.
- [[chunking]] — The author explicitly states that large context windows eliminate the need for chunking in their memex system, thereby avoiding potential issues like retrieval hallucination associated with fragmented information.
- [[retrieval_hallucination]] — The author suggests that eliminating chunking through the use of a large context window helps prevent retrieval hallucination in their memex system, ensuring more accurate and reliable knowledge synthesis.
- [[homelab]] — The author uses a 'Proxmox homelab' to run a local agent via OpenClaw, indicating a preference for self-hosting and local control over certain components of their memex system, aligning with a hands-on approach.

## Contradictions or open questions
None identified.

## Source
memex_vision_linkedin.md


## Related Synthesis
- [[architecting_the_future_of_lloyds_a_comparison_of_multi_agent_systems_and_event_driven_architecture]]