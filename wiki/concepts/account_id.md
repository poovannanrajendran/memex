---
title: "Account ID"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-11-02
confidence: medium
---

## Definition
An Account ID is a unique identifier for a specific account or login instance within a communication channel that supports multiple accounts (e.g., different WhatsApp numbers or Slack workspaces).

## Why it matters (in Poovi's context)
It allows OpenClaw to differentiate between multiple instances of the same communication channel. This enables routing messages from distinct accounts (like a personal vs. business WhatsApp number) to separate agents.

## Key properties or components
- Identifies channel accounts
- Used in bindings
- Supports multiple logins per channel
- e.g., 'personal' vs 'biz' WhatsApp

## Contradictions or debates
None.

## Sources
- [[multi_agent_routing_openclaw]]

## Related concepts
- [[binding]]
- [[channel]]
- [[agent]]
- [[routing]]
- [[whatsapp]]
