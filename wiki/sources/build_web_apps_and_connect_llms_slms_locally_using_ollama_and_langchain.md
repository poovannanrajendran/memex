---
title: "Build Web Apps and connect LLM's & SLM's locally using Ollama and LangChain"
source_type: youtube
url: "https://www.youtube.com/watch?v=mNKOKnSbG4Q"
ingested: 2026-04-23
confidence: high
tags: ["AI", "LLM", "SLM", "Ollama", "LangChain", "Flask", "Web Development", "Multimodal AI", "Local Hosting", "Phi", "LLaVA", "SQLite", "Python"]
---

## Summary
This video demonstrates how to build a multimodal web application using Flask, LangChain, and Ollama. The application can connect to locally hosted Large Language Models (LLMs) and Small Language Models (SLMs). It showcases the ability to process both text and image inputs, using specific models like Phi for text generation and LLaVA for image analysis, with conversation history stored in SQLite.

## Key claims
- It's possible to build multimodal applications using locally hosted LLMs and SLMs.
- Flask, LangChain, and Ollama are effective tools for creating such applications.
- The application can distinguish between text-only prompts and prompts that include images, using different models accordingly.
- Conversation threads can be stored locally using SQLite and SQLAlchemy.
- Ollama simplifies the process of running LLMs locally, and LangChain makes it easy to integrate AI capabilities into applications.

## Entities mentioned
- [[flask]] — It is the primary framework used to build the single-page web application demonstrated in the video.
- [[ollama]] — Ollama is used to host and run the LLMs and SLMs locally, making them accessible to the Flask application.
- [[langchain]] — LangChain is used to connect to and interact with the locally hosted LLMs and SLMs within the Flask application.
- [[phi]] — Phi is one of the locally hosted models used by the application for text-based interactions.
- [[llava]] — LLaVA is used as the vision model within the application to process and describe uploaded images.
- [[sqlite]] — SQLite is used to store conversation threads and history locally for the web application.
- [[sqlalchemy]] — SQLAlchemy is used in conjunction with SQLite to manage and write conversation data.

## Concepts covered
- [[large_language_model_llm]] — LLMs are the core AI components driving the conversational and analytical capabilities of the application, enabling it to process and generate human-like text.
- [[small_language_model_slm]] — SLMs, like Phi, offer a more resource-efficient way to integrate language processing capabilities into applications, particularly when local hosting is desired.
- [[multimodal_applications]] — This concept is central to the video's demonstration, showcasing an application that handles both text and image inputs, enabling richer user interactions.
- [[local_hosting]] — The video emphasizes local hosting using Ollama, which is crucial for privacy, cost-effectiveness, and demonstrating the feasibility of running sophisticated AI models without external dependencies.
- [[web_application_development]] — The video illustrates practical web application development by building a user interface with Flask to interact with AI models.

## Contradictions or open questions
None identified.

## Source
mNKOKnSbG4Q_Build_Web_Apps_and_connect_LLM_s___SLM_s_locally_u.txt
