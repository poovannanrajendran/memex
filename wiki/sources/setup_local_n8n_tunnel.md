---
title: "Setup Local n8n Tunnel"
source_type: youtube
url: "https://www.youtube.com/watch?v=QQ-V10sM3gI"
ingested: 2026-04-23
confidence: high
tags: ["n8n", "Cloudflare", "Tunnel", "AI", "Automation", "Self-hosted", "Docker", "Containerization", "Localhost", "LLM"]
---

## Summary
This video explains how to set up a Cloudflare tunnel to make a local n8n instance publicly accessible. It details how services within a containerized environment, like n8n, Postgress, Quadrant, and Olama, can communicate with each other but are otherwise blocked by firewalls. A Cloudflare tunnel acts as a public address, enabling external services like Telegram to send data to the local n8n instance.

## Key claims
- A Cloudflare tunnel can expose a local n8n instance to the public internet.
- Containerized applications like n8n, Postgress, Quadrant, and Olama can communicate internally but are blocked by external firewalls.
- Cloudflare tunnels bypass local firewalls to allow external services to communicate with local applications.

## Entities mentioned
- [[cloudflare]] — Provides the tunneling service to make local applications publicly accessible.
- [[n8n]] — The local application that needs to be made publicly accessible via a tunnel.
- [[olama]] — One of the self-hosted AI starter kit components running in the Docker container.
- [[postgress]] — One of the self-hosted AI starter kit components running in the Docker container.
- [[quadrant]] — One of the self-hosted AI starter kit components running in the Docker container.

## Concepts covered
- [[cloudflare_tunnel]] — Enables secure public accessibility of local AI development environments like n8n without complex network configurations.
- [[containerization]] — Used to bundle n8n and its related AI tools (Postgress, Quadrant, Olama) into a single, manageable environment for local development.
- [[localhost]] — Represents the default way to access local applications before making them publicly accessible.
- [[ai_starter_kit]] — Provides a foundation for building and running AI-related workflows and applications locally.

## Contradictions or open questions
None identified.

## Source
QQ-V10sM3gI_Setup_Local_n8n_Tunnel__explained_simply____aiagen.txt
