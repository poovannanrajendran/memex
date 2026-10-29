---
title: "One Guy Keeps Breaking Every AI Model on Launch Day"
source_type: youtube
url: "https://www.youtube.com/watch?v=KomryzIaIog"
ingested: 2026-10-29
confidence: medium
tags: ["AI jailbreak", "cybersecurity", "prompt engineering", "AI safety"]
---

## Summary
A YouTube video discusses how a hacker known as 'Pliny the Liberator' consistently bypasses safety features in AI models upon their release. The video explains the technical reasons behind these vulnerabilities, such as AI's tokenisation process, the nature of safety training as a probability adjustment rather than a knowledge deletion, and the sheer combinatorial possibilities of language that outstrip safety training data. It highlights how unusual formatting and split prompts can trick AI into revealing restricted information or performing unintended actions.

## Key claims
- A single individual, 'Pliny the Liberator', has repeatedly demonstrated the ability to 'jailbreak' major AI models on their launch days.
- Jailbreaking involves eliciting responses from AI that it is programmed to refuse, using only text prompts without actual system hacking.
- AI safety training is often a probability overlay on core knowledge, not a deletion of that knowledge, making it susceptible to prompts that bypass the safety layer.
- Unusual text formatting (like 'leetspeak') or encoding can obscure prompts from safety training, even if the AI understands the underlying meaning.
- The vastness of language token combinations means safety training data can only cover a tiny fraction of potential inputs.
- Harmful outputs can be reconstructed from seemingly harmless pieces, making even split prompts a viable jailbreaking method.

## Entities mentioned
- [[pliny_the_liberator]] — The central figure demonstrating AI vulnerabilities, whose actions prompt the discussion and analysis within the video.
- [[openai]] — Developer of AI models that are frequently targeted and demonstrated as vulnerable by Pliny the Liberator.
- [[grok]] — An example of an AI model that Pliny the Liberator has successfully jailbroken.
- [[claude_opus_5_5]] — An example of an AI model that Pliny the Liberator has exploited, demonstrating vulnerabilities even in safety-conscious systems.

## Concepts covered
- [[ai_jailbreaking]] — It reveals fundamental limitations in current AI safety mechanisms and highlights the ongoing challenge of controlling AI behaviour, posing risks for misinformation and misuse.
- [[prompt_engineering]] — It is the primary method used to interact with and control AI, and advanced prompt engineering is key to both utilising AI's capabilities and, as demonstrated, exploiting its weaknesses (jailbreaking).
- [[tokenisation]] — It is a fundamental step in how AI understands and generates text. Differences in tokenisation, especially when combined with unusual phrasing or encoding, can be exploited to bypass safety filters that are trained on different token representations.
- [[ai_safety_training]] — Crucial for ensuring AI is used responsibly, but as demonstrated, it's not foolproof and can be bypassed. Understanding its limitations is key to improving AI safety.

## Contradictions or open questions
The video presents a paradox where the very nature of AI's vast knowledge and desire to be helpful is precisely what makes it vulnerable to misuse, directly challenging the efficacy of current safety training methods.

## Source
KomryzIaIog_One_Guy_Keeps_Breaking_Every_AI_Model_on.md
