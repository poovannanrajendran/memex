---
title: "BeamNG.drive"
entity_type: product
tags: ["product"]
last_updated: 2026-04-23
---

## Overview
BeamNG.drive is a soft-body physics simulator known for its realistic vehicle damage and simulation. It is very CPU-intensive, especially when simulating multiple vehicles or complex scenarios.

## Role in this knowledge base
Tested to showcase the workstation's capability with CPU-bound simulations, highlighting potential NUMA issues.

## Key facts
- In BeamNG.drive, simulating 24 cars caused performance to drop below 10 FPS due to a NUMA issue where one CPU was maxed out while the other was idle.

## Sources
- [[the_ultimate_budget_workstation]]

## Related concepts
- [[physics_simulation]]
- [[cpu_intensive]]
- [[numa_architecture]]
