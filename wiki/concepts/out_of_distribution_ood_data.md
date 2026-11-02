---
title: "Out of Distribution (OOD) Data"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-11-02
confidence: medium
---

## Definition
Data that significantly differs from the data a machine learning model was trained on. When an AI encounters OOD data, its performance may degrade, and its predictions can become unreliable, as it has not learned how to handle such inputs.

## Why it matters (in Poovi's context)
Explains why certain novel or unusual prompt variations (like 'leetspeak' or hidden characters) can bypass an AI's safety training, as these inputs were likely not part of the original safety dataset.

## Key properties or components
- Deviates from training data
- Can cause model performance degradation
- Challenging for safety protocols
- Exploited by adversarial attacks

## Contradictions or debates
None.

## Sources
- [[one_guy_keeps_breaking_every_ai_model_on_launch_day]]

## Related concepts
- [[ai_jailbreaking]]
- [[adversarial_attacks]]
- [[machine_learning_robustness]]
