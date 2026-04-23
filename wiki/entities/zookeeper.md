---
title: "Zookeeper"
entity_type: tool
tags: ["tool"]
last_updated: 2026-04-23
---

## Overview
Apache ZooKeeper is a centralised service for maintaining configuration information, naming, providing distributed synchronisation, and providing group services. It was traditionally used by Kafka for coordination.

## Role in this knowledge base
An external dependency previously required for Kafka to manage its brokers, elect leaders, and coordinate configurations.

## Key facts
- Newer versions of Kafka (3.0+) use KRaft to remove the need for Zookeeper.

## Sources
- [[kafka_tutorial_for_beginners_everything_you_need_to_get_started]]

## Related concepts
- [[distributed_coordination]]
- [[broker_management]]
