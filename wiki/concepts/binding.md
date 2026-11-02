---
title: "Binding"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-11-02
confidence: medium
---

## Definition
A binding in OpenClaw is a configuration rule that maps a communication channel account (e.g., a specific WhatsApp number or Slack workspace) to a particular agent. These bindings dictate how inbound messages are routed.

## Why it matters (in Poovi's context)
Bindings are the mechanism that enables multi-agent routing. They determine which agent receives and processes messages from specific channels or accounts, ensuring communications reach the intended AI persona.

## Key properties or components
- Maps channel account to agent
- Defines routing rules
- Can specify channel, accountId, peer, guildId
- Most-specific rule wins (tie-breaking)
- AND semantics for multiple match fields

## Contradictions or debates
None.

## Sources
- [[multi_agent_routing_openclaw]]

## Related concepts
- [[agent]]
- [[gateway]]
- [[routing]]
- [[channels]]
- [[account_id]]
