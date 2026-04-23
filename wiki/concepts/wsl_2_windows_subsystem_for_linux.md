---
title: "WSL 2 (Windows Subsystem for Linux)"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-23
confidence: high
---

## Definition
A feature of Windows that allows developers to run a Linux environment, including most command-line tools, utilities, and applications, directly on Windows, unmodified, without the overhead of a traditional virtual machine. WSL 2 offers better performance and full system call compatibility.

## Why it matters (in Poovi's context)
Used as a method to run LLMs on a Windows machine with access to a dedicated Nvidia GPU (4080), demonstrating GPU passthrough capabilities.

## Key properties or components
- Linux compatibility on Windows
- GPU passthrough
- Improved performance over WSL 1
- System call compatibility

## Contradictions or debates
None.

## Sources
- [[run_local_llms_on_hardware_from_50_to_50_000_we_test_and_compare]]

## Related concepts
- [[nvidia_4080]]
- [[ollama]]
- [[gpu_acceleration]]
