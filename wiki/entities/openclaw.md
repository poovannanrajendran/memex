---
title: "OpenClaw"
entity_type: tool
tags: [ai-agent, homelab, self-hosted]
last_updated: 2026-04-20
---

## Overview
OpenClaw is Poovi's self-hosted personal AI agent gateway. It runs on a dedicated VM in his Proxmox homelab (ai-node-01) and connects to various LLM providers (OpenAI, DeepSeek, Google Gemini, etc.).

## Role in this knowledge base
A core part of Poovi's personal AI infrastructure. It is used for daily assistant tasks, ops monitoring, and command execution via Telegram. It is designed to be compatible with standardisation layers like [[agentic_stack]].

## Key facts
- Primary model: DeepSeek.
- Infrastructure: 12 vCPU / 24GB RAM on Proxmox VE.
- Accessible via Telegram bot and browser dashboard over Tailscale.

## Sources
- [[07_homelab]]
- [[09_ai_collaboration]]
- [[agentic_stack_overview]]

## Related concepts
- [[agentic_stack]]
- [[llm_wiki_pattern]]
