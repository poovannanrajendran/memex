---
title: "Run Local LLMs on Hardware from $50 to $50,000 - We Test and Compare!"
source_type: youtube
url: "https://www.youtube.com/watch?v=mUGsv_IHT-g"
ingested: 2026-04-23
confidence: high
tags: ["LLM", "Local LLM", "Ollama", "Llama 3.1", "Raspberry Pi", "Mini PC", "Gaming PC", "Workstation", "AI Hardware", "GPU", "CPU", "Performance Comparison", "DIY AI", "Tech Review", "YouTube"]
---

## Summary
This video tests the performance of running local Large Language Models (LLMs) like Llama 3.1 on a wide range of hardware, from a $50 Raspberry Pi to a $50,000 Dell workstation. The analysis compares setup processes and inference speeds across different systems, including budget Mini PCs, gaming rigs, and high-end AI workstations, with a focus on whether the LLMs can effectively utilise GPUs or rely solely on CPUs.

## Key claims
- Local LLMs can be run on hardware ranging from $50 Raspberry Pi to $50,000 AI workstations.
- Performance varies significantly based on hardware, with higher-end systems offering much faster inference times.
- Raspberry Pi can run LLMs, but performance is impractically slow for real-time use.
- Some Mini PCs with integrated AMD GPUs (like the Radeon 780M) may not fully support GPU acceleration for LLMs due to compatibility issues with current software.
- Dedicated NVIDIA GPUs (e.g., RTX 4080, RTX 6000 Ada) paired with sufficient RAM significantly improve LLM performance.
- Larger models (e.g., 405 billion parameters) require substantial RAM and can still be slow even on high-end hardware, highlighting the trade-off between model size and performance.
- The efficiency of the LLM model itself (e.g., Llama 3.2 vs. Llama 3.1) also impacts performance, with smaller, more efficient models running faster.

## Entities mentioned
- [[raspberry_pi_4]] — The Raspberry Pi 4 was used as the lowest-cost hardware to test the feasibility of running a local LLM, demonstrating the baseline performance limitations.
- [[ollama]] — Ollama is the primary software used across all tested hardware to download and run the Llama models, serving as the core LLM inference engine.
- [[llama_3_1]] — Llama 3.1 (specifically the 70 billion parameter version for most tests) was the primary LLM tested for its performance on different hardware configurations.
- [[herk_from_orion]] — This Mini PC represents a mid-range consumer-grade option tested for running LLMs locally, specifically highlighting its integrated GPU capabilities and direct Windows installation.
- [[amd_radeon_780m]] — This iGPU was tested for its potential to accelerate LLM inference on the Herk Mini PC, but it encountered compatibility issues with Ollama.
- [[dell_threadripper_workstation]] — This was the workstation used in a previous episode, criticised for not being budget-friendly, and it serves as a reference point for high-end performance.
- [[nvidia_4080]] — This GPU was tested on a Threadripper system to evaluate its capability in running local LLMs, demonstrating strong performance when properly configured with WSL2.
- [[mac_pro_m2_ultra]] — This machine was tested to assess LLM performance leveraging its unified memory architecture, which allows the GPU to access a large pool of system RAM.
- [[overclocked_96_core_threadripper]] — This represents the pinnacle of the hardware tested, used to run the largest version of the Llama model (405 billion parameters), to demonstrate the limits of local LLM deployment.
- [[nvidia_6000_ada]] — This professional-grade GPU was paired with a 96-core Threadripper to test the performance of the largest Llama model (405 billion parameters).
- [[llama_3_1_405_billion_parameters]] — This massive model was run on the most powerful workstation to demonstrate the extreme hardware requirements for very large LLMs.
- [[dell]] — Dell provided the high-end $50,000 AI workstation for testing, representing the top tier of hardware capability for running local LLMs.
- [[meta_ai]] — Meta AI is the developer of the Llama models, which are the subject of the performance tests in the video.
- [[jeff_bezos]] — Mentioned as a potential character for a new story generation task, illustrating the creative capabilities of LLMs.

## Concepts covered
- [[large_language_model_llm]] — The core technology being tested in the video, with the aim of running it locally on personal hardware.
- [[local_llm_inference]] — The central theme of the video, exploring the feasibility and performance of running LLMs locally across a wide spectrum of hardware.
- [[gpu_acceleration]] — Crucial for achieving usable performance with LLMs; the video investigates which hardware configurations successfully leverage GPU acceleration.
- [[cpu_inference]] — Tested as a fallback when GPU acceleration is not possible or insufficient, particularly on low-end hardware like the Raspberry Pi.
- [[unified_memory]] — Tested on the Mac Pro M2 Ultra to see if its unified memory architecture allows the GPU to efficiently handle large LLMs.
- [[wsl_2_windows_subsystem_for_linux]] — Used as a method to run LLMs on a Windows machine with access to a dedicated Nvidia GPU (4080), demonstrating GPU passthrough capabilities.
- [[model_parameter_count]] — A key factor influencing LLM performance and hardware requirements, as demonstrated by testing models of different sizes (e.g., 70B vs. 405B parameters).

## Contradictions or open questions
None identified.

## Source
mUGsv_IHT-g_Run_Local_LLMs_on_Hardware_from__50_to__50_000___W.txt
