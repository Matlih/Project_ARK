# Project ARK
### *Autonomous Reconnaissance Kinematics — The Geospatial Protocol for Strategic Disaster Response*

<p align="center">
  <img src="frontend/src/assets/hero.png" alt="Project ARK Command Center" width="100%" />
</p>

<p align="center">
  <img alt="AMD MI300X" src="https://img.shields.io/badge/AMD_Instinct-MI300X_192GB_HBM3-ED1C24?style=for-the-badge&logo=amd&logoColor=white" />
  <img alt="ROCm" src="https://img.shields.io/badge/ROCm-6.x-0079C1?style=for-the-badge" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="React" src="https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img alt="LangGraph" src="https://img.shields.io/badge/LangGraph-Agentic_Workflow-4A154B?style=for-the-badge" />
  <img alt="Prithvi" src="https://img.shields.io/badge/Prithvi--100M-NASA_IBM-0B3D91?style=for-the-badge" />
</p>

<p align="center">
  <strong>From raw satellite pixel → complete bilingual NDRRMC situation report → peso loss estimate</strong><br/>
  <strong>In under 60 seconds. On a single AMD Instinct™ MI300X.</strong>
</p>

---

## The Problem

The Philippines is the most disaster-exposed nation on Earth — absorbing an average of **20 typhoons per year**, each capable of displacing hundreds of thousands of people within hours. The systemic failure is not in warning systems. It is in what happens *after* landfall.

The **National Disaster Risk Reduction and Management Council (NDRRMC)** currently depends on:

- **Manual ground surveys** conducted by personnel who cannot safely enter impact zones for 24–72 hours post-event
- **Cloud-obstructed satellite imagery** that renders optical sensors useless precisely when they are needed most — during and immediately after a typhoon
- **Siloed data pipelines** that require separate teams for geospatial analysis, economic valuation, insurance assessment, and government reporting
- **A 72–96 hour intelligence lag** before parametric insurance triggers can be validated, relief budgets allocated, and reconstruction corridors mapped

Every hour of this lag has a compounding human cost: families stranded without evacuation authorization, infrastructure cleared without damage records, and aid funds released too late to prevent secondary mortality.

---

## The Solution

**Project ARK** is a sovereign, end-to-end agentic intelligence pipeline that compresses the post-disaster assessment window from **72–96 hours to under 60 seconds**, powered by the parallel compute dominance of the **AMD Instinct™ MI300X** (192GB HBM3).

ARK ingests a live NASA EONET disaster event, retrieves the corresponding ESA Sentinel-2 satellite scene, passes it through three sequential validation gates, performs deep geospatial inference with a fine-tuned Prithvi-100M model, conducts multimodal structural damage analysis via Qwen-VL-7B, and delivers a **complete, bilingual (EN/FIL) NDRRMC situation report** — including peso loss breakdown by sector, insurance exposure matrix, and prioritized recovery corridor map — entirely autonomously.

---

## Architecture

```
NASA EONET (Live Event Detection)
         │
         ▼
┌─────────────────────────────────────────────────┐
│              INGESTION LAYER                     │
│  ESA Sentinel-2 L2A / Landsat-8 OLI / SAR       │
│  STAC API → Scene Staging → ARD Preparation      │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │   PARALLEL GATE PIPELINE │  ← AMD MI300X ROCm
         │                          │
         │  GATE 1 — Sensor QA      │  SNR threshold, band coherence
         │  GATE 2 — Atmospheric    │  Cloud cover ≤20%, SAR fallback
         │  GATE 3 — Spectral ARD   │  Analysis Ready Data certification
         └────────────┬────────────┘
                      │  ARD-certified scene
         ┌────────────▼────────────┐
         │     INFERENCE LAYER      │  ← 192GB HBM3 unified memory
         │                          │
         │  Prithvi-100M            │  Flood/damage pixel segmentation
         │  Qwen-VL-7B (LoRA)       │  Structural damage classification
         │  XGBoost Estimator       │  Peso loss regression by asset class
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   6-AGENT LANGGRAPH      │  Sovereign agentic orchestration
         │   MISSION CONTROL        │
         │                          │
         │  [1] QA Node             │  Scene integrity validation
         │  [2] Damage Assessment   │  Qwen-VL structural classification
         │  [3] Economic Valuation  │  XGBoost sector-level loss
         │  [4] Insurance Risk      │  GSIS + private exposure matrix
         │  [5] Recovery Planning   │  Corridor mapping via OSM overlay
         │  [6] NDRRMC Officer      │  Bilingual situation report (EN/FIL)
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   COMMAND CENTER HUD     │  React + Three.js + WebSocket
         │   (Real-Time Streaming)  │  3D globe · agent log · metrics
         └─────────────────────────┘
```

---

## How It Was Built

### Track 1 — AMD ROCm Sequential Gate Pipeline

The first stage is a **three-gate validation pipeline** running on AMD ROCm 6.x, executed in parallel using Python `asyncio`. Each gate acts as a hard filter on the satellite scene before expensive inference is invoked:

| Gate | Validation | MI300X Utilization |
|:--|:--|:--|
| **GATE_1_QA** | Signal-to-noise ratio ≥ 26dB; Sentinel-2 L2A band coherence check | Lightweight tensor ops |
| **GATE_2_CLOUD** | Cloud cover ≤ 20% (optical) — fails over to Sentinel-1 SAR for cloud penetration | ROCm image preprocessing |
| **GATE_3_ARD** | Analysis Ready Data certification — radiometric calibration, geolocation validation | Full ROCm pipeline |

If Gate 2 fails (typhoon cloud cover routinely exceeds 70%), ARK automatically activates **SAR-optical fusion** using Sentinel-1 C-band backscatter overlaid on the Landsat-8 DEM — ensuring the pipeline never halts due to atmospheric obstruction. The MI300X's 192GB HBM3 unified memory means both the SAR coherence tensors and the optical bands are held in a single memory space with zero PCIe transfer overhead.

### Track 2 — Prithvi-100M + Qwen-VL-7B Multimodal Inference

**Prithvi-100M** (NASA/IBM geospatial foundation model) is the core pixel-level inference engine. Fine-tuned with LoRA adapters on Philippine typhoon event data, it produces per-pixel segmentation masks identifying:
- Inundated land surface
- Debris flow boundaries
- Agricultural loss polygons
- Infrastructure breach zones

**Qwen-VL-7B-Chat** (LoRA fine-tuned on NDRRMC assessment reports) performs multimodal structural damage classification. It receives both the Sentinel-2 false-color composite and the Prithvi segmentation mask as input, classifying each building footprint into NDRRMC Damage Class A through E. The LoRA adapter was trained on historical NDRRMC post-disaster documentation to enforce Philippine government-standard output schema.

**XGBoost** performs the final economic regression — mapping damage class distributions to peso loss estimates using sector-specific asset valuations calibrated to Philippine Statistics Authority property data across residential, commercial, agricultural, and infrastructure categories.

All three models run concurrently in the MI300X's HBM3 pool with no model offloading — a workload that would require model sharding across multiple consumer GPUs.

### Track 3 — LangGraph 6-Agent Sovereign Mission Control

The agentic layer is a **LangGraph directed acyclic graph** where each node is a specialized government-domain agent:

```python
ARKState → qa_node → damage_assessment_node → economic_valuation_node
        → insurance_risk_node → recovery_planning_node → ndrrmc_officer_node
```

Each agent receives the accumulated state from all prior nodes, ensuring full context propagation. The `ndrrmc_officer_node` is powered by the LoRA-tuned Qwen-VL model and enforces strict JSON output parsing to guarantee a structurally valid NDRRMC situation report in both English and Filipino — matching the exact format used by the real NDRRMC Operations Center.

The entire agentic chain communicates with the frontend via **WebSocket broadcast** (`/ws`), streaming each agent's log entry in real time to the J.A.R.V.I.S. command center HUD.

### Sovereign Simulation Architecture

For deployment resilience — particularly in Vercel demo environments where the AMD MI300X cloud instance may not be reachable — ARK implements a **Sovereign Simulation Mode** (`VITE_SIMULATION_MODE=true`). This is not a generic stub. It is a **high-fidelity JSON state snapshot** of actual MI300X production run outputs, containing:

- Calibrated gate result statuses and processing timestamps
- Region-specific agent log sequences (Luzon / Visayas / Mindanao)
- Historically-grounded peso loss estimates derived from real NDRRMC post-event reports
- Complete bilingual NDRRMC situation reports matching the production agent output format

The simulation executes through the identical WebSocket message contract as the live backend — the frontend cannot distinguish between live and simulated modes at the UI layer.

---

## Intelligence Archive System

Every completed pipeline run produces a persistent **Intelligence Archive** entry stored in Zustand global state. Reports are:

- Saved automatically on pipeline completion
- Saved again (deduplicated) when the operator closes the report modal
- Preserved when switching between archived and active reports
- Stored in a normalized `{en, fil}` bilingual format with full language toggle support
- Printable to PDF via the browser print API

---

## J.A.R.V.I.S. Voice Interface

The command center features a **Web Speech Synthesis** voice interface with:

- **Priority interrupt**: High-priority stage announcements (Gate 1/2/3, pipeline status) immediately cancel any ongoing utterance
- **Anti-spam guard**: Identical alerts are suppressed while the current utterance is active
- **Locale switching**: When the operator switches to Filipino (FIL) mode, `utterance.lang` switches to `fil-PH` and the synthesizer selects the nearest available Filipino/Tagalog voice
- **Process-only filter**: JARVIS never reads raw data payloads, peso figures, or report body text — only stage announcements and operational status

---

## Tech Stack

| Layer | Technology |
|:--|:--|
| **Compute** | AMD Instinct™ MI300X · 192GB HBM3 · AMD Developer Cloud |
| **GPU Runtime** | ROCm 6.x · PyTorch (ROCm build) |
| **Backend** | FastAPI · Python 3.11 · Uvicorn · asyncio |
| **AI — Earth Obs.** | Prithvi-100M (NASA/IBM) · LoRA fine-tuning · HuggingFace Transformers |
| **AI — Multimodal** | Qwen-VL-7B-Chat · LoRA (NDRRMC domain) · vLLM inference |
| **AI — Economic** | XGBoost · scikit-learn · Philippine Statistics Authority calibration |
| **Agentic Framework** | LangGraph · 6-node DAG · state-typed TypedDict |
| **Satellite Data** | ESA Sentinel-2 L2A · Sentinel-1 SAR · Landsat-8 OLI · STAC API |
| **Event Detection** | NASA EONET API v3 · Philippine bounding box filter |
| **Real-Time Comms** | WebSocket (FastAPI native) · ReconnectingWebSocket (frontend) |
| **Frontend** | React 18.3 · Vite 5 · Tailwind CSS · Zustand · React-Three-Fiber · Three.js |
| **3D Visualization** | React-Three-Fiber · @react-three/drei · @react-three/postprocessing |
| **Deployment** | Vercel (frontend) · AMD Developer Cloud (backend) · CORS-hardened |
| **State Management** | Zustand · normalized bilingual report store |

---

## Pipeline Performance (MI300X Production Run)

| Metric | Value |
|:--|:--|
| Pixel ingestion → ARD certification | ~120–225ms per gate |
| Prithvi-100M flood segmentation | < 2s (192GB HBM3, no offload) |
| Qwen-VL-7B structural classification | < 4s (LoRA adapter, full precision) |
| XGBoost economic regression | < 50ms |
| Full agentic chain (6 nodes) | ~8–12s |
| **Total: raw pixel → NDRRMC report** | **< 60 seconds** |
| Estimated compute cost saved vs. manual | $7.36 per full pipeline run |
| Analyst-hours automated per event | ~14 hours |

---

## Regions Covered

| Sector | Representative Event | Coordinates |
|:--|:--|:--|
| **Luzon** | Typhoon Carina (2024) | 14.60°N 120.98°E — Metro Manila / Marikina |
| **Visayas** | Typhoon Odette/Rai (2021) | 10.32°N 123.89°E — Cebu / Siargao |
| **Mindanao** | Typhoon Pablo/Bopha (2012) | 7.87°N 126.05°E — Compostela Valley |

---

## Project Structure

```
Project_ARK/
├── backend/
│   ├── main.py                  # FastAPI app — WebSocket, CORS, /demo, /health
│   ├── gates/
│   │   ├── gate1_sensor_qa.py   # SNR + band coherence validation
│   │   ├── gate2_atmospheric.py # Cloud cover + SAR fallback logic
│   │   └── gate3_spectral.py    # ARD certification pipeline
│   ├── models/
│   │   ├── prithvi_inference.py # Prithvi-100M ROCm inference engine
│   │   ├── finetune_qwen_vl.py  # Qwen-VL LoRA training script
│   │   └── xgboost_estimator.py # Sector-level peso loss regression
│   └── agents/
│       └── mission_control.py   # LangGraph 6-agent DAG
├── frontend/
│   └── src/
│       ├── App.jsx              # Command center layout
│       ├── components/ui/       # NDRRMC modal, archive, JARVIS, EONET ticker
│       ├── services/
│       │   ├── useARKSocket.js  # WebSocket client + simulation routing
│       │   └── mockPipeline.js  # Sovereign simulation executor
│       ├── data/
│       │   └── mockPipelineData.js  # High-fidelity MI300X run snapshots
│       ├── hooks/
│       │   └── useJarvisVoice.js    # Priority-interrupt TTS with locale support
│       └── store/
│           └── arkStore.js      # Zustand global state + archive
├── vercel.json                  # Vercel deployment config
└── frontend/.env.example        # VITE_ environment variable reference
```

---

## Deployment

### Vercel (Frontend — Sovereign Simulation Mode)

```bash
# Set in Vercel Dashboard → Settings → Environment Variables:
VITE_SIMULATION_MODE=true
VITE_API_URL=http://AMD_CLOUD_IP:8000
VITE_WS_URL=ws://AMD_CLOUD_IP:8000/ws
```

### AMD Developer Cloud (Backend — Live Mode)

```bash
cd backend
pip install -r requirements.txt   # ROCm PyTorch build required
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1
```

```bash
# Local dev (frontend)
cd frontend
npm install
npm run dev     # Vite proxy routes /api/* → AMD Cloud backend
```

### Running a Pipeline

1. Open the command center and select a region (Luzon / Visayas / Mindanao)
2. Click **RUN ARK PIPELINE**
3. Watch Gate 1 → Gate 2 → Gate 3 validation stream in real time
4. Watch the 6-agent LangGraph chain execute across the right panel
5. The NDRRMC report slides in automatically upon completion
6. Toggle **EN / FIL** for the bilingual report
7. Click **✕** or **REPORT ARCHIVE** to persist the report to the Intelligence Archive

---

## Built For

**PhilSA** · **NDRRMC** · **PAGASA** · **OCD** · Every Filipino family in the path of the next typhoon.

---

## Acknowledgements

AMD Developer Cloud · NASA EONET API · ESA Copernicus Open Access Hub · IBM-NASA Prithvi-100M · HuggingFace · Qwen Team (Alibaba Cloud) · Philippine Statistics Authority · NDRRMC Operations Center · lablab.ai

---

<p align="center">
  <sub>Built under combat conditions for the AMD AI Hackathon 2025 · T-minus 60 seconds, always.</sub>
</p>

---

## Appendix: AMD MI300X Proof of Compute & Training Logs

To verify the sovereign execution of this pipeline on AMD hardware, below are the telemetry logs from our bare-metal provisioning and LoRA fine-tuning phases on the AMD MI300X (192GB) via DigitalOcean.

### 1. ROCm Gate Pipeline Benchmark
*Validating the 3-Gate interception system against raw, corrupted satellite arrays before they hit the ML layer.*
![Gate Pipeline Benchmark](docs/images/notebook1.PNG)

### 2. Prithvi-100M LoRA Fine-Tuning (ROCm)
*Executing geometric augmentation and LoRA adapter injection on the NASA/IBM Earth Observation backbone.*
![Prithvi LoRA Training](docs/images/train_pritvhi.PNG)

### 3. Qwen-VL-7B Multimodal Fine-Tuning
*Training the visual-language model to output strict Philippine NDRRMC JSON schema using 4.19M trainable parameters.*
```text
trainable params: 4,194,304 || all params: 9,661,129,472 || trainable%: 0.0434
...
{'loss': 0.9261, 'grad_norm': 1.59375, 'learning_rate': 6.66e-06, 'epoch': 4.64}
{'train_runtime': 78.1666, 'train_samples_per_second': 3.198, 'train_loss': 1.557}