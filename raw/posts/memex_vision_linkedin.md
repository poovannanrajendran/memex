---
title: "Building memex — The Vision and Tech Stack"
source_type: post
platform: LinkedIn
date: 2026-04-20
---

## Post 1: The Vision
After 30 apps in 30 days — I realised I had a different problem. I was consuming more information than ever. Research papers. Podcast transcripts. YouTube talks. Market articles. And retaining almost none of it in a useful, connected form.

Notes scattered everywhere. Ideas that never linked up. The same insight re-discovered three weeks later. Classic knowledge problem. Except most tools just give you better folders.

So I started building memex. The name matters. Vannevar Bush coined "memex" in 1945 — a hypothetical device where an individual stores all their knowledge, so it can be retrieved and associated at speed. A machine extension of human memory. 80 years later, with a 1M-token context window and an AI agent as the librarian — we can actually build it.

The problem with standard knowledge tools: RAG systems retrieve. They don't reason across sources. They don't resolve contradictions. They don't compound. I wanted something closer to how a research librarian actually works — ingesting, cross-linking, synthesising — not just searching.

## Post 2: The Tech Stack
Building memex — my AI-maintained second brain. Here's what's powering it under the hood. Why Google's ecosystem for this? One word: context.

Gemini 2.5 Pro has a 1M+ token context window. For a knowledge system where synthesis across sources is the entire point — loading a full research paper, long transcript, or multi-document set in a single pass changes the architecture entirely. No chunking. No retrieval hallucination. One-shot analysis.

The stack:
- Gemini CLI — agent runtime.
- Gemini 2.5 Pro — long-document ingestion, synthesis, contradiction resolution.
- Gemini 2.5 Flash — short article ingest, wiki health checks.
- Python 3.12 — automation scripts: ingest.py, lint.py, synthesise.py.
- Obsidian — the human-facing interface.
- Git — audit trail.
- Proxmox homelab — local agent via OpenClaw.
