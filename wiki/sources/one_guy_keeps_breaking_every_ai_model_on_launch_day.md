---
title: "One Guy Keeps Breaking Every AI Model on Launch Day"
source_type: youtube
url: "https://www.youtube.com/watch?v=KomryzIaIog"
ingested: 2026-11-02
confidence: medium
tags: ["AI jailbreak", "cybersecurity", "prompt engineering", "AI models", "AI safety"]
---

## Summary
This video explores how a hacker known as 'Pliny the Liberator' consistently bypasses the safety features of AI models upon their release. It explains the technical concept of AI jailbreaking, where prompts are crafted to elicit responses that the AI is trained to refuse. The video highlights that AI safety is a learned behaviour rather than an inherent block, which Pliny exploits by using techniques like 'leetspeak' and hidden characters to confuse the safety training.

## Key claims
- A hacker named Pliny the Liberator has repeatedly 'jailbroken' new AI models on their launch days for over two years.
- Jailbreaking involves getting an AI to bypass its safety protocols using only text-based prompts, without hacking servers.
- AI safety training is a learned behaviour that increases the probability of refusing harmful requests, rather than a strict knowledge block.
- Techniques like using obscure language (e.g., 'leetspeak') or hidden characters can confuse AI safety mechanisms because the refusal training hasn't encountered these specific 'out of distribution' inputs.
- Even with robust safety training, AI models can be exploited because their underlying knowledge base remains intact, and prompts can be crafted to bring out previously learned information.
- Harmful outputs can sometimes be reconstructed from seemingly harmless pieces, making complete prevention difficult.

## Entities mentioned
- [[pliny_the_liberator]] — The primary subject of the video, demonstrating vulnerabilities in AI safety measures.
- [[openai]] — Developer of AI models that are frequently targeted and jailbroken by Pliny.
- [[grok]] — An example of an AI model that Pliny has successfully jailbroken.
- [[claude_opus_5_5]] — An example of an AI model that Pliny has targeted, and which has also been used in red teaming exercises to extract harmful information.

## Concepts covered
- [[ai_jailbreaking]] — It highlights potential vulnerabilities in AI safety protocols and demonstrates how AI models can be made to produce unintended or harmful content, posing risks for AI deployment.
- [[prompt_engineering]] — Crucial for both maximising the utility of AI tools and for understanding how security vulnerabilities like jailbreaking are exploited.
- [[ai_safety_training]] — Fundamental to ensuring AI systems are deployed responsibly and do not cause harm. Understanding its limitations is key to assessing AI security.
- [[out_of_distribution_ood_data]] — Explains why certain novel or unusual prompt variations (like 'leetspeak' or hidden characters) can bypass an AI's safety training, as these inputs were likely not part of the original safety dataset.

## Contradictions or open questions
The claim that AI safety is merely a 'habit painted on top' of core knowledge, rather than a fundamental constraint, could be seen as a contradiction to the strong safety assurances often given by AI developers. The ease with which seemingly complex models can be bypassed by simple prompt manipulation also challenges the current state of AI security.

## Source
KomryzIaIog_One_Guy_Keeps_Breaking_Every_AI_Model_on.md
