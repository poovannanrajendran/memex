---
title: "KRaft"
entity_type: tool
tags: ["tool"]
last_updated: 2026-04-23
---

## Overview
KRaft (Kafka Raft metadata mode) is a new protocol built into Kafka that removes the need for an external Zookeeper cluster for metadata management and coordination.

## Role in this knowledge base
The successor to Zookeeper for Kafka's internal coordination, simplifying its architecture and management.

## Key facts
- Introduced in Kafka version 3.0, KRaft allows Kafka to manage its own metadata and elect leaders internally.

## Sources
- [[kafka_tutorial_for_beginners_everything_you_need_to_get_started]]

## Related concepts
- [[distributed_consensus]]
- [[metadata_management]]
