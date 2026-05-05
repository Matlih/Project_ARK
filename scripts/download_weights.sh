#!/bin/bash

# ==========================================
# Project ARK - Model Weight Acquisition
# ==========================================

# 1. Parse Arguments (--config-only)
CONFIG_ONLY=0
if [[ "$1" == "--config-only" ]]; then
    CONFIG_ONLY=1
    echo "⚠️  Running in CONFIG-ONLY mode. Large tensor/safetensors files will be skipped."
fi

# 2. Load Environment Variables (.env)
if [ -f .env ]; then
    # Export variables from .env ignoring comments
    export $(grep -v '^#' .env | xargs)
fi

# 3. Security Check: HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo "❌ ERROR: HF_TOKEN environment variable is not set."
    echo "Create a .env file in the root directory and add: HF_TOKEN=hf_your_token_here"
    exit 1
fi

# 4. Dependency Check: huggingface-cli
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ ERROR: huggingface-cli is not installed."
    echo "Run: pip install huggingface_hub"
    exit 1
fi

# Authenticate with Hugging Face silently
huggingface-cli login --token $HF_TOKEN --add-to-git-credential=false > /dev/null 2>&1

# ==========================================
# Core Download Function
# ==========================================
download_model() {
    local repo_id=$1
    local dest_dir=$2
    local est_size=$3

    echo "----------------------------------------"
    echo "🎯 Target: $repo_id"
    echo "📂 Destination: $dest_dir"

    # Check if directory exists and is not empty
    if [ -d "$dest_dir" ] && [ "$(ls -A $dest_dir 2>/dev/null)" ]; then
        echo "✅ Directory populated. Skipping download to prevent overwrite."
        return
    fi

    mkdir -p "$dest_dir"

    if [ $CONFIG_ONLY -eq 1 ]; then
        echo "📦 Estimated Size (Config/Tokenizers Only): < 15MB"
        # Only pull json, text, and python files. Ignore heavy binaries.
        huggingface-cli download "$repo_id" \
            --local-dir "$dest_dir" \
            --local-dir-use-symlinks False \
            --include "*.json" "*.txt" "*.md" "*.py"
    else
        echo "📦 Estimated Size (Full Weights): $est_size"
        # Pull the entire repository
        huggingface-cli download "$repo_id" \
            --local-dir "$dest_dir" \
            --local-dir-use-symlinks False
    fi
    echo "✅ Download complete for $repo_id."
}

# ==========================================
# Execute Payload
# ==========================================

# Model 1: Prithvi-100M (Damage Classification)
download_model "ibm-nasa-geospatial/Prithvi-100M" "data/weights/prithvi-100m" "~400MB"

# Model 2: Qwen-VL-Chat (NDRRMC Reporter Agent)
if [ $CONFIG_ONLY -eq 0 ]; then
    echo "⚠️ WARNING: Qwen-VL is massive. Ensure you are on the AMD Cloud or have fast internet."
    download_model "Qwen/Qwen-VL-Chat" "data/weights/qwen-vl-7b" "~19GB"
else
    download_model "Qwen/Qwen-VL-Chat" "data/weights/qwen-vl-7b" "< 10MB"
fi

# Model 3: SegFormer-B2 (Cloud Screening / Fmask base)
download_model "nvidia/mit-b2" "data/weights/segformer-b2" "~100MB"

# ==========================================
# Final System Report
# ==========================================
echo "----------------------------------------"
echo "📊 Total Disk Usage for data/weights/:"
du -sh data/weights/
echo "========================================"
echo "✅ Weight acquisition complete. Project ARK is primed."