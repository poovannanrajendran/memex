---
title: "NUMA (Non-Uniform Memory Access)"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-23
confidence: high
---

## Definition
A computer memory architecture where memory access times depend on the memory location relative to the processor. In multi-socket systems, processors have faster access to their local memory banks than to memory attached to other processors.

## Why it matters (in Poovi's context)
Demonstrated as a potential performance issue in the build when running non-NUMA aware software (like BeamNG.drive), leading to one CPU being overloaded while the other remained idle.

## Key properties or components
- Multiple memory controllers
- Local vs. remote memory access
- Performance implications for multi-socket systems
- Requires software optimisation

## Contradictions or debates
None.

## Sources
- [[the_ultimate_budget_workstation]]

## Related concepts
- [[multi_socket_systems]]
- [[server_architecture]]
- [[software_optimisation]]
