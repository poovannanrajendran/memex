---
title: "Microsoft Agent Framework Overview"
source_type: article
url: "https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python"
tags: ["ai-agents", "microsoft", "autogen", "semantic-kernel", "orchestration"]
---

# Microsoft Agent Framework Overview

Microsoft Agent Framework offers two primary categories of capabilities:

| | Description |
| :--- | :--- |
| **Agents** | Individual agents that use LLMs to process inputs, call tools and MCP servers, and generate responses. Supports Microsoft Foundry, Anthropic, Azure OpenAI, OpenAI, Ollama, and more. |
| **Workflows** | Graph-based workflows that connect agents and functions for multi-step tasks with type-safe routing, checkpointing, and human-in-the-loop support. |

The framework also provides foundational building blocks, including model clients (chat completions and responses), an agent session for state management, context providers for agent memory, middleware for intercepting agent actions, and MCP clients for tool integration. Together, these components give you the flexibility and power to build interactive, robust, and safe AI applications.

## Why Agent Framework?

Agent Framework combines AutoGen's simple agent abstractions with Semantic Kernel's enterprise features — session-based state management, type safety, middleware, telemetry — and adds graph-based workflows for explicit multi-agent orchestration.

Semantic Kernel and AutoGen pioneered the concepts of AI agents and multi-agent orchestration. The Agent Framework is the direct successor, created by the same teams. It combines AutoGen's simple abstractions for single- and multi-agent patterns with Semantic Kernel's enterprise-grade features such as session-based state management, type safety, filters, telemetry, and extensive model and embedding support. 

Beyond merging the two, Agent Framework introduces workflows that give developers explicit control over multi-agent execution paths, plus a robust state management system for long-running and human-in-the-loop scenarios.

In short, Agent Framework is the next generation of both Semantic Kernel and AutoGen.
