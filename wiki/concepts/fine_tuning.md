---
title: "Fine-tuning"
domain: ai-engineering
tags: ["ai-engineering"]
last_updated: 2026-04-23
confidence: high
---

## Definition
Fine-tuning involves further training a pre-trained foundation model on a custom dataset of prompt-completion pairs. This process adapts the model to specific styles, tones, tasks, or knowledge domains, improving its performance and predictability for particular use cases.

## Why it matters (in Poovi's context)
Fine-tuning is vital for instilling intuition, specific writing styles, or achieving higher performance from smaller, more efficient models. It allows for 'baking in' behaviours that are difficult to specify through prompts alone.

## Key properties or components
- Training on Example Data
- Updating Model Weights
- Instilling Style and Tone
- Parameter-Efficient Fine-Tuning (PEFT)
- Instruction Tuning
- Safety Tuning

## Contradictions or debates
A common misconception is that fine-tuning is solely for teaching facts; however, the video clarifies that RAG is better suited for factual recall, while fine-tuning excels at behaviour, style, and intuition. Another misconception is that it requires massive datasets or is prohibitively expensive, which is no longer true with modern techniques like PEFT and smaller datasets (e.g., 20 examples).

## Sources
- [[prompt_engineering_rag_and_fine_tuning_benefits_and_when_to_use]]

## Related concepts
- [[large_language_models]]
- [[foundation_models]]
- [[prompt_engineering]]
- [[retrieval_augmented_generation]]
- [[few_shot_learning]]
