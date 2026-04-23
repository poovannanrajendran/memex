---
title: "Broker"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-23
confidence: high
---

## Definition
A Kafka server that is part of the Kafka cluster. Brokers store data (events) in topics and partitions, handle producer requests, and serve consumer requests.

## Why it matters (in Poovi's context)
Brokers are the backbone of a Kafka cluster, responsible for storing and managing the event data and ensuring its availability.

## Key properties or components
- Stores data on disk
- Handles read/write requests
- Replicates data for fault tolerance
- Part of a Kafka cluster

## Contradictions or debates
None.

## Sources
- [[kafka_tutorial_for_beginners_everything_you_need_to_get_started]]

## Related concepts
- [[kafka_cluster]]
- [[topic]]
- [[partition]]
- [[replication]]
