#!/bin/bash

echo "=========================================="
echo "Initializing Project ARK Deployment on MI300X"
echo "=========================================="

# 1. Detect ROCm GPU
echo -e "\n[1/5] Checking Hardware..."
if command -v rocm-smi &> /dev/null; then
    rocm-smi
else
    echo "NO GPU (rocm-smi not found). Proceeding with CPU-only mode."
fi

# 2. Install Python Dependencies with ROCm Index
echo -e "\n[2/5] Installing Dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt --extra-index-url https://download.pytorch.org/whl/rocm6.0

# Install vLLM separately as requested
echo "Installing vLLM..."
pip install vllm

# 3. Spin up Redis (Idempotent)
echo -e "\n[3/5] Checking Redis Container..."
if [ "$(docker ps -q -f name=^/redis$)" ]; then
    echo "Redis is already running."
else
    echo "Starting Redis..."
    docker rm -f redis 2>/dev/null
    docker run -d --name redis -p 6379:6379 redis:7-alpine
fi

# 4. Spin up Postgres (Idempotent)
echo -e "\n[4/5] Checking PostgreSQL Container..."
if [ "$(docker ps -q -f name=^/postgres$)" ]; then
    echo "Postgres is already running."
else
    echo "Starting Postgres..."
    docker rm -f postgres 2>/dev/null
    docker run -d --name postgres \
        -e POSTGRES_PASSWORD=arkpass \
        -e POSTGRES_DB=projectark \
        -p 5432:5432 \
        postgres:16
fi

# 5. Verify PyTorch GPU Visibility
echo -e "\n[5/5] Verifying PyTorch ROCm Integration..."
python3 -c "
import torch
print('GPU Available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('Device Name:', torch.cuda.get_device_name(0))
else:
    print('Device Name: None')
"

echo -e "\n=========================================="
echo "✅ PROJECT ARK ENVIRONMENT READY"
echo "=========================================="