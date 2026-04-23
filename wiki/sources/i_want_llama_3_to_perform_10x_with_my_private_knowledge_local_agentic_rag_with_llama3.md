---
title: "I want Llama 3 to perform 10x with my private knowledge - Local Agentic RAG with llama3"
source_type: youtube
url: "https://www.youtube.com/watch?v=u5Vcrwpzoz8"
ingested: 2026-04-23
confidence: high
tags: ["RAG", "Agentic RAG", "LLM", "Llama 3", "Local LLM", "LangGraph", "LlamaIndex", "Data Parsing", "Vector Database", "Knowledge Management", "AI Agents"]
---

## Summary
This video explores advanced Retrieval Augmented Generation (RAG) techniques to improve the performance of large language models (LLMs) when using private knowledge. It highlights the limitations of basic RAG and introduces methods such as better data parsing with tools like Llama-Parser and FireCrawl, optimizing chunk sizes, re-ranking retrieved documents, and implementing agentic RAG. Agentic RAG leverages AI agents to dynamically decide the optimal RAG pipeline, including query translation and self-correction, leading to more reliable and accurate responses, albeit with potentially longer processing times.

## Key claims
- Knowledge Management is a key value proposition for AI in organizations due to the vast amounts of unstructured documentation.
- Basic RAG implementations often struggle with real-world data complexity (e.g., tables, charts, mixed data types) and retrieval accuracy.
- Advanced RAG tactics, including improved data parsing, chunk size optimization, re-ranking, and agentic approaches, are crucial for building production-ready RAG applications.
- Agentic RAG allows dynamic adaptation of the RAG pipeline using AI agents for tasks like query translation, planning, and self-correction, enhancing accuracy at the cost of speed.
- Tools like Llama-Parser, FireCrawl, and frameworks like LangGraph, combined with local LLMs like Llama 3, enable the creation of sophisticated, locally run agentic RAG systems.

## Entities mentioned
- [[llama_3]] — The video focuses on using Llama 3 as the decision-making model within a local agentic RAG system.
- [[llama_parser]] — It addresses the challenge of extracting information accurately from complex PDF documents, including tables and diagrams, for RAG systems.
- [[firecrawl]] — It is used to efficiently ingest and structure website content for RAG systems, reducing noise and preparing metadata.
- [[langgraph]] — It is used to define the high-level workflow and logic for the agentic RAG system, enabling LLMs to complete tasks at each stage.
- [[tavily]] — It is used as a tool within the agentic RAG system for performing web searches when necessary, such as during self-correction or when retrieved local documents are insufficient.
- [[ollama]] — It facilitates the local execution of Llama 3, enabling the development and testing of local RAG applications without relying on cloud APIs.
- [[llamaindex]] — The organisation developed Llama-Parser and is a key player in advancing RAG techniques, with expertise in handling private knowledge for LLMs.

## Concepts covered
- [[retrieval_augmented_generation_rag]] — Crucial for enabling LLMs to access and utilize private or up-to-date information, improving accuracy and relevance beyond their training data.
- [[agentic_rag]] — Allows for more sophisticated and adaptable RAG systems that can handle complex queries, self-correct errors, and optimize the retrieval process.
- [[vector_database]] — Forms the backbone of the retrieval phase in RAG, enabling efficient searching for semantically similar information to a given query.
- [[chunk_size_optimization]] — Affects the balance between providing sufficient context for the LLM and avoiding the 'lost in the middle' problem within limited context windows.
- [[data_parsing]] — Essential for preparing raw data into a usable format for LLMs and RAG systems, especially when dealing with diverse and complex file types.
- [[knowledge_management]] — AI, particularly LLMs and RAG, offers powerful solutions to overcome the challenges of managing vast amounts of unstructured organizational data.

## Contradictions or open questions
None identified.

## Source
u5Vcrwpzoz8__I_want_Llama3_to_perform_10x_with_my_private_know.txt
