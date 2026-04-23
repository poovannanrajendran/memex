---
title: "Tight Coupling"
domain: general
tags: ["general"]
last_updated: 2026-04-23
confidence: high
---

## Definition
A condition where one component of a system is highly dependent on another component. In microservices, this means services directly call each other and rely on their immediate availability, leading to cascading failures.

## Why it matters (in Poovi's context)
Identified as a primary problem in traditional microservice architectures that Kafka aims to solve by introducing an intermediary broker.

## Key properties or components
- High dependency between services
- Impact of one service failure on others
- Difficulty in independent updates

## Contradictions or debates
None.

## Sources
- [[kafka_tutorial_for_beginners_everything_you_need_to_get_started]]

## Related concepts
- [[microservices_architecture]]
- [[loose_coupling]]
