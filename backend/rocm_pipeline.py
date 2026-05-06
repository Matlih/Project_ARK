import sys
import time
import torch
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Import the existing gates
from backend.gates.gate1_sensor_qa import run_gate1
from backend.gates.gate2_atmospheric import run_gate2
from backend.gates.gate3_spectral import run_gate3

def verify_rocm_setup() -> dict:
    """Verifies the AMD ROCm ecosystem and PyTorch bindings."""
    gpu_available = torch.cuda.is_available()
    
    if gpu_available:
        device_name = torch.cuda.get_device_name(0)
        total_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    else:
        device_name = "CPU (No CUDA/ROCm detected)"
        total_memory_gb = 0.0

    # torch.version.hip will return the ROCm version if compiled for AMD, else None
    rocm_version = getattr(torch.version, 'hip', "N/A")

    return {
        "gpu_available": gpu_available,
        "device_name": device_name,
        "total_memory_gb": round(total_memory_gb, 2),
        "rocm_version": rocm_version
    }

class ParallelGatePipeline:
    def __init__(self):
        """Initializes the MI300X asynchronous execution streams."""
        # Note: On a local Windows machine without an AMD/NVIDIA GPU, 
        # PyTorch will gracefully default these to dummy CPU streams.
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if self.device.type == "cuda":
            self.stream1 = torch.cuda.Stream()
            self.stream2 = torch.cuda.Stream()
            self.stream3 = torch.cuda.Stream()
        else:
            self.stream1 = None
            self.stream2 = None
            self.stream3 = None

    def run_sequential(self, scene_dir: str) -> tuple:
        """Baseline sequential execution for speedup comparison."""
        t0 = time.perf_counter()
        g1 = run_gate1(scene_dir)
        g2 = run_gate2(scene_dir)
        g3 = run_gate3(scene_dir)
        t1 = time.perf_counter()
        return (g1, g2, g3), (t1 - t0) * 1000

    def run_parallel(self, scene_dir: str, event_id: str) -> dict:
        """Launches all 3 gates simultaneously across Python threads and PyTorch Streams."""
        
        # 1. Capture baseline sequential time
        _, seq_time_ms = self.run_sequential(scene_dir)
        
        # 2. Parallel Execution Wrappers
        def _exec_g1():
            if self.stream1:
                with torch.cuda.stream(self.stream1):
                    return run_gate1(scene_dir)
            return run_gate1(scene_dir)

        def _exec_g2():
            if self.stream2:
                with torch.cuda.stream(self.stream2):
                    return run_gate2(scene_dir)
            return run_gate2(scene_dir)

        def _exec_g3():
            if self.stream3:
                with torch.cuda.stream(self.stream3):
                    return run_gate3(scene_dir)
            return run_gate3(scene_dir)

        # 3. Dispatch the streams concurrently
        t0 = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future1 = executor.submit(_exec_g1)
            future2 = executor.submit(_exec_g2)
            future3 = executor.submit(_exec_g3)
            
            g1 = future1.result()
            g2 = future2.result()
            g3 = future3.result()

        # Synchronize the MI300X to ensure all streams hit the finish line
        if self.device.type == "cuda":
            torch.cuda.synchronize()
            
        t1 = time.perf_counter()
        parallel_time_ms = (t1 - t0) * 1000

        passes_g1 = g1.status in ["PASS", "PARTIAL_PASS"]
        passes_g2 = g2.status in ["PASS", "PARTIAL_PASS"]
        passes_g3 = g3.status in ["PASS", "PARTIAL_PASS"]
        ard_certified = passes_g1 and passes_g2 and passes_g3

        return {
            "gate1": g1,
            "gate2": g2,
            "gate3": g3,
            "ard_certified": ard_certified,
            "total_time_ms": round(parallel_time_ms, 2),
            "sequential_time_ms": round(seq_time_ms, 2),
            "speedup_factor": round(seq_time_ms / parallel_time_ms if parallel_time_ms > 0 else 1.0, 2)
        }

    def benchmark(self, scene_dir: str, n_runs: int = 5) -> dict:
        """Stress tests the architecture to generate MI300X proof metrics."""
        print(f"Executing {n_runs} parallel benchmark runs...")
        
        parallel_times = []
        sequential_times = []
        
        for _ in range(n_runs):
            res = self.run_parallel(scene_dir, "bench_001")
            parallel_times.append(res["total_time_ms"])
            sequential_times.append(res["sequential_time_ms"])
            
        mean_par = np.mean(parallel_times)
        mean_seq = np.mean(sequential_times)
            
        return {
            "mean_ms": round(float(mean_par), 2),
            "std_ms": round(float(np.std(parallel_times)), 2),
            "min_ms": round(float(np.min(parallel_times)), 2),
            "max_ms": round(float(np.max(parallel_times)), 2),
            "mean_sequential_ms": round(float(mean_seq), 2),
            "speedup_vs_sequential": round(float(mean_seq / mean_par), 2)
        }

if __name__ == "__main__":
    print("==========================================")
    print("🛰️ PROJECT ARK - ROCm Architecture Test")
    print("==========================================\n")
    
    # 1. Verify Ecosystem
    setup = verify_rocm_setup()
    print("--- ROCm / CUDA Telemetry ---")
    for k, v in setup.items():
        print(f"  {k}: {v}")
    print("\n")
    
    if len(sys.argv) < 2:
        print("Usage: python backend/rocm_pipeline.py <path_to_SAFE_folder>")
        sys.exit(1)
        
    target_path = sys.argv[1]
    pipeline = ParallelGatePipeline()
    
    # 2. Run Benchmark
    stats = pipeline.benchmark(target_path, n_runs=5)
    
    print("\n--- Benchmark Results ---")
    print(f"Parallel Mean:   {stats['mean_ms']} ms")
    print(f"Sequential Mean: {stats['mean_sequential_ms']} ms")
    print(f"Speedup Factor:  {stats['speedup_vs_sequential']}x")