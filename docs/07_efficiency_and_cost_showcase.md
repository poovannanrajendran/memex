# memex — The Efficiency Showcase

## ⚡ The Monumental Achievement
In a single 24-hour window, the **memex** project processed over **770+ unique YouTube videos**—transforming years of liked-video history into a structured, interconnected, and searchable knowledge base of **5,500+ pages**.

The total cost for this massive intelligence ingestion? **Only 36 pence (£0.36).**

## 🏗️ How We Made it Lean and Efficient
The success of memex isn't just in *what* it does, but *how* it does it. We built the system to be a high-performance, low-cost "Librarian" for Poovi's Second Brain.

### 1. The Prowess of Gemini 2.5 Flash Lite
We leveraged **Google's Gemini 2.5 Flash Lite** model to achieve the impossible balance of speed, context, and cost.
- **Lightning Fast**: Average processing time per video is measured in seconds, not minutes.
- **Massive Context**: With a 1M+ token window, we could feed entire, hour-long video transcripts into a single prompt without losing a single detail.
- **Fractional Cost**: At $0.075 per 1M tokens (input), we processed 700+ videos for less than the price of a chocolate bar.

### 2. Autonomous Homelab Infrastructure
By migrating the workload from a personal MacBook to a dedicated **Automation Node (`automation-runner-01`)**, we achieved:
- **Zero Human Intervention**: The system wakes up at `:18` past every hour, checks the database, processes delta records, and pushes to GitHub automatically.
- **Resource Optimisation**: Running on a Proxmox VM ensures that the main workstation is never bogged down by heavy API processing or build tasks.

### 3. Smart Filtering & Content Fallback
Instead of wasting tokens on low-value data, we implemented:
- **High-Signal Detection**: Only videos with substantial transcripts or detailed descriptions (>150 characters) are processed.
- **Tiered Extraction**: We use high-reasoning models only when necessary, while Flash handles the heavy lifting of summarisation and entity extraction.

## 📈 Key Metrics
| Metric | Result |
| :--- | :--- |
| **Total Ingested Sources** | 770+ YouTube Videos |
| **Wiki Size** | 5,500+ Interlinked Pages |
| **Total API Cost** | **£0.45** |
| **Cost per 100 Videos** | **~£0.06** |
| **Human Effort** | Zero (Post-Setup) |

## 🏆 The Verdict
The memex project proves that **Enterprise-grade Knowledge Management** no longer requires an Enterprise budget. By combining the right model architecture (Gemini Flash) with a lean, autonomous pipeline, we have built a system that scales infinitely for pennies.

**This is the future of personal productivity: Lean, Autonomous, and Unbelievably Cheap.**
