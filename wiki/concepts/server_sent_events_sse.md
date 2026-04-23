---
title: "Server-Sent Events (SSE)"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-23
confidence: high
---

## Definition
Server-Sent Events is a standard that allows a web server to push data to a web client over a single, long-lived HTTP connection. It's a unidirectional communication from server to client.

## Why it matters (in Poovi's context)
n8n's MCP trigger utilizes SSE, which is relevant for enabling real-time communication between the n8n workflow and external MCP hosts, though it may require specific configurations or gateways like Super Gateway for compatibility with certain clients.

## Key properties or components
- Unidirectional communication (server to client)
- Uses HTTP connection
- Enables real-time updates

## Contradictions or debates
None.

## Sources
- [[n8n_just_released_native_mcp_trigger_and_ai_agent_tool_official_walkthrough]]

## Related concepts
- [[mcp]]
- [[webhooks]]
- [[api]]
