# 🛰️ Project ARK
**The Geospatial Protocol for Strategic Disaster Kinematics**

![AMD MI300X](https://img.shields.io/badge/AMD-MI300X-black?style=flat-square&logo=amd)
![ROCm 6.x](https://img.shields.io/badge/ROCm-6.x-blue?style=flat-square)
![PhilSA](https://img.shields.io/badge/Partner-PhilSA-blue?style=flat-square)
![NDRRMC](https://img.shields.io/badge/Partner-NDRRMC-red?style=flat-square)
![3-Track](https://img.shields.io/badge/Hackathon-3_Track_Attack-orange?style=flat-square)

## The 60-Second Promise
From a raw satellite pixel to a complete NDRRMC situation report with peso loss estimates — in under 60 seconds. Powered by the parallel processing dominance of the AMD Instinct™ MI300X.

## The Problem
* **The Bottleneck:** The Philippine NDRRMC currently relies on manual, on-the-ground damage assessment following catastrophic typhoons.
* **The Lag:** Traditional economic intelligence gathering and parametric insurance triggering takes 72 to 96 hours.
* **The Solution:** Project ARK executes this entire pipeline autonomously in 60 seconds.

## Architecture

* **Gates:** ROCm-accelerated pre-processing screens Sentinel-2 imagery for atmospheric interference.
* **Analysis:** Prithvi-100M and Qwen-VL extract multimodal damage polygons and infrastructure context.
* **Agents:** A 6-agent LangGraph system calculates peso loss and structures government reports.
* **Dashboard:** A lag-free, 3D interactive command center streaming live intelligence.

## Tech Stack
* **Hardware:** AMD Instinct™ MI300X (192GB HBM3 VRAM) | ROCm 6.0
* **Backend:** FastAPI | PostgreSQL | Redis
* **AI & Vision:** Prithvi-100M (HuggingFace/NASA) | Qwen-VL-7B-Chat | XGBoost | Fmask
* **Agentic Framework:** LangGraph | CrewAI
* **Frontend:** React.js | Vite | Tailwind CSS | Zustand | React-Three-Fiber

## 3-Track Attack
| Track | Component | Status |
| :--- | :--- | :--- |
| **Track 1** | 6-Agent Mission Control | ✅ |
| **Track 2** | Prithvi LoRA + Qwen-VL LoRA + XGBoost | ✅ |
| **Track 3** | Sentinel-2 + Prithvi + Qwen-VL Multimodal | ✅ |

## Built For
PhilSA · NDRRMC · PAGASA · Philippine disaster survivors.

## Acknowledgements
AMD Developer Cloud · NASA EONET · ESA Copernicus · IBM-NASA Prithvi · lablab.ai
