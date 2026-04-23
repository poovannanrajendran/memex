---
title: "18 Weird and Wonderful ways I use Docker"
source_type: youtube
url: "https://www.youtube.com/watch?v=RUqGlWr5LBA"
ingested: 2026-04-23
confidence: high
tags: ["Docker", "Containerization", "Development", "DevOps", "Security", "Hacking", "Productivity", "Linux", "WSL2", "GUI Applications", "Server Management", "AI", "Scientific Computing", "Virtualization"]
---

## Summary
The video explores 18 diverse and often unconventional uses for Docker, a containerization platform. The presenter, Chuck, demonstrates how Docker can be used for everyday tasks like running web browsers and note-taking applications, to more complex applications such as security research, scientific computing (Folding at Home), and even setting up isolated hacking labs. The content highlights Docker's flexibility, security benefits through isolation, and ease of use, often in conjunction with tools like Docker Desktop and its extensions, and emphasizes its utility for managing dependencies and creating reproducible environments.

## Key claims
- Docker can be used to run full graphical web browsers within containers, providing isolation and security.
- Applications like Obsidian and LibreOffice can be containerized for easy access and data persistence.
- Docker enables running distributed computing projects like Folding at Home, contributing to research.
- Docker provides a lightweight and manageable alternative to virtual machines for application isolation.
- Docker containerization enhances security by isolating applications and their dependencies from the host OS.
- Docker Scout is a tool for analysing container images for vulnerabilities, improving security.
- Docker Networks and Docker Compose are powerful features for creating and managing complex, isolated environments like hacking labs.
- Docker allows for the easy testing and running of various operating systems and even emulated hardware like Raspberry Pi.
- Building custom Docker images using Dockerfiles provides a 'superpower' for creating tailored development and tool environments.
- Docker Desktop, with its extensions like Portainer, offers a user-friendly graphical interface for managing containers.

## Entities mentioned
- [[docker]] — The primary subject of the video, demonstrating its versatility and numerous applications.
- [[linuxserver_io]] — Provides many of the container images demonstrated in the video for applications like web browsers, Obsidian, and LibreOffice.
- [[chasm_vnc]] — Enables GUI access to containerized applications demonstrated in the video, such as web browsers and Obsidian.
- [[chasm]] — Develops Chasm VNC, a key tool used in the video for accessing containerized applications.
- [[obsidian]] — Demonstrated as an application that can be effectively run inside a Docker container for access and data persistence.
- [[libreoffice]] — Showcased as an application that can be containerized and accessed via a web browser, offering a full office suite solution.
- [[folding_at_home]] — Demonstrated as a scientific research application that can be run within a Docker container, leveraging system resources for beneficial computation.
- [[nvidia]] — Relevant due to the discussion of enabling GPU acceleration for Docker containers, specifically for Folding at Home, and the need for NVIDIA's container runtime.
- [[docker_desktop]] — Presented as a user-friendly graphical interface for managing Docker containers, images, and settings, including extensions.
- [[portainer]] — Highlighted as a powerful Docker extension available within Docker Desktop, greatly enhancing the management of containerized environments.
- [[danger_zone]] — Demonstrated as a security-focused application that leverages Docker containers to safely process untrusted documents.
- [[fabric]] — Used as a specific example to demonstrate the process of building a custom Docker image and running it as a container.
- [[chatgpt]] — Mentioned as a tool that assisted in creating the example Dockerfile and is a modern alternative to some older tools.
- [[docker_scout]] — Presented as a vital tool for ensuring the security of Docker images and containers, helping to identify and remediate vulnerabilities.
- [[kali_linux]] — Demonstrated as a powerful security tool that can be run within a Docker container, ideal for setting up isolated hacking labs.
- [[damn_vulnerable_web_application_dvwa]] — Used as an example of a vulnerable machine that can be deployed as a Docker container within an isolated network for ethical hacking practice.
- [[rocky_linux]] — Shown as an example of how to easily spin up and test different operating systems like Rocky Linux within Docker containers.
- [[raspberry_pi_os]] — Demonstrated as an operating system that can be emulated and run within a Docker container, showcasing Docker's versatility.
- [[tools_that_i_found]] — Showcased as a collection of useful IT tools that are conveniently deployed and accessed through a Docker container.

## Concepts covered
- [[docker]] — The central concept of the video, demonstrating its wide-ranging applications from simple utilities to complex development environments and security labs.
- [[containerization]] — The core technology enabling all the use cases demonstrated in the video, providing isolation, portability, and efficiency.
- [[gui_graphical_user_interface]] — The video shows how Docker can enable GUI applications, which normally require direct OS interaction, to be run and accessed remotely or via a browser.
- [[isolation]] — A key security and stability benefit of Docker, preventing applications and their dependencies from conflicting with each other or the host system.
- [[dependency_management]] — Docker simplifies dependency management by packaging everything an application needs into a container, avoiding 'dependency hell' and environment configuration issues.
- [[dockerfile]] — Enables users to define and build their own custom container images, providing immense flexibility and control over application environments.
- [[docker_compose]] — Simplifies the deployment and management of applications composed of multiple containers, such as complex development or testing environments.
- [[docker_networks]] — Crucial for setting up secure and isolated environments, such as hacking labs, by controlling network access between containers and the host.
- [[container_security]] — A critical consideration when deploying containers, especially for sensitive applications or when using third-party images. Tools like Docker Scout help address this.
- [[hacking_lab]] — Docker provides an efficient and isolated way to set up and tear down complex hacking labs, allowing for experimentation without risk to production systems.
- [[virtual_machine_vm]] — Docker is often presented as a lighter-weight and more efficient alternative to VMs for many use cases, offering similar isolation benefits with less overhead.
- [[gpu_acceleration]] — Enables computationally intensive tasks within Docker containers, such as AI model training or scientific research like Folding at Home, to run much faster by leveraging dedicated GPU hardware.

## Contradictions or open questions
None identified.

## Source
RUqGlWr5LBA_18_Weird_and_Wonderful_ways_I_use_Docker.txt
