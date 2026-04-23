---
title: "CPU Inference"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-23
confidence: high
---

## Definition
Running a large language model using only the Central Processing Unit (CPU) for computations. This is generally slower than GPU inference, especially for complex models, but requires no specialized graphics hardware.

## Why it matters (in Poovi's context)
Tested as a fallback when GPU acceleration is not possible or insufficient, particularly on low-end hardware like the Raspberry Pi.

## Key properties or components
- Slower processing
- Higher CPU utilisation
- No VRAM dependency
- Lower hardware barrier

## Contradictions or debates
None.

## Sources
- [[run_local_llms_on_hardware_from_50_to_50_000_we_test_and_compare]]

## Related concepts
- [[raspberry_pi]]
- [[ollama]]
- [[gpu_acceleration]]
