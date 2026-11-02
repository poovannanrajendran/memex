---
title: "Multi-agent routing - OpenClaw"
source_type: article
url: "https://docs.openclaw.ai/concepts/multi-agent"
ingested: 2026-11-02
confidence: medium
tags: ["multi-agent", "routing", "openclaw", "agent", "gateway", "channels", "bindings"]
---

## Summary
This article explains how OpenClaw's Gateway can host and manage multiple isolated agents, each with its own workspace, state, and session history. It details how 'bindings' route inbound messages from various channel accounts (like WhatsApp or Slack) to the appropriate agent based on rules. The system allows for distinct personas, separate authentication, and distinct session management for each agent, enabling multiple distinct conversational AIs to run concurrently on a single server.

## Key claims
- OpenClaw's Gateway can run multiple isolated agents concurrently.
- Each agent has its own dedicated workspace, state directory, and session history.
- Bindings are used to route incoming messages from channel accounts to specific agents.
- An agent is defined as a full per-persona scope, including workspace, state, and session store.
- Multiple agents can be configured to handle different personas, accounts, or even different WhatsApp numbers.
- Routing rules are deterministic and follow a most-specific-match wins hierarchy.
- Each agent can have its own sandbox and tool configuration for security and resource control.

## Entities mentioned
- [[openclaw]] — The subject of the article, detailing its multi-agent routing capabilities.
- [[gateway]] — The infrastructure that enables multi-agent functionality in OpenClaw.
- [[agentdir]] — Represents the persistent storage location for an individual agent's state.
- [[agents_md]] — Defines an agent's persona and rules within its workspace.
- [[soul_md]] — Contributes to defining an agent's unique identity and behaviour within its workspace.
- [[user_md]] — Stores optional user-specific information within an agent's workspace.
- [[whatsapp]] — An example of a communication channel that can be integrated with OpenClaw for multi-agent routing.
- [[slack]] — An example of a communication channel that can be integrated with OpenClaw.

## Concepts covered
- [[agent]] — Agents are the fundamental units managed by OpenClaw's Gateway. The ability to isolate and manage multiple agents is key to the platform's multi-agent routing capabilities, allowing for distinct AI personalities and functionalities.
- [[binding]] — Bindings are the mechanism that enables multi-agent routing. They determine which agent receives and processes messages from specific channels or accounts, ensuring communications reach the intended AI persona.
- [[gateway]] — The Gateway is the core infrastructure that enables the multi-agent system. It provides the runtime environment and management layer for all hosted agents.
- [[workspace]] — The workspace isolates an agent's files and configurations, contributing to its unique persona and operational context. It's a key component of agent isolation.
- [[account_id]] — It allows OpenClaw to differentiate between multiple instances of the same communication channel. This enables routing messages from distinct accounts (like a personal vs. business WhatsApp number) to separate agents.
- [[qmd_memory_search]] — Enables agents to recall and utilise information from past conversations, potentially across different agents, to inform current responses. It enhances contextual awareness and memory recall.
- [[sandboxing]] — Crucial for managing untrusted agents, controlling resource consumption, and implementing flexible security policies on a per-agent basis. It enhances the overall security and stability of the multi-agent system.

## Contradictions or open questions
The article mentions that agent workspaces are not hard sandboxes by default, which could be seen as a contradiction to the concept of agent isolation if not explicitly managed with sandboxing features.

## Source
multi_agent_routing_openclaw.md
