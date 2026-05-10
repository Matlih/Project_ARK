import asyncio
import logging
import random # Mocking logic for demo

# These imports must match your file names in the screenshot
from backend.gates.gate1_sensor_qa import run_gate1
from backend.gates.gate2_atmospheric import run_gate2
from backend.gates.gate3_spectral import run_gate3

class ParallelGatePipeline:
    def __init__(self):
        self.logger = logging.getLogger("GATE_PIPELINE")

    async def run_parallel(self, scene_dir: str):
        """Runs all three validation gates concurrently."""
        self.logger.info(f"Initiating Parallel Gate Pipeline for: {scene_dir}")
        
        # We wrap the gate functions in tasks to run them in parallel
        # Note: If your individual gate files don't have 'async' functions yet, 
        # we call them using asyncio.to_thread or just mock the delay for the demo.
        
        tasks = [
            self._execute_gate("GATE_1_QA", 0.8),
            self._execute_gate("GATE_2_ATMOSPHERIC", 1.5),
            self._execute_gate("GATE_3_SPECTRAL", 1.2)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Format the output for the WebSocket and Mission Control
        return results

    async def _execute_gate(self, name, delay):
        """Simulates gate execution with a delay for the UI to feel 'real'."""
        await asyncio.sleep(delay)
        
        # Logic: Gate 2 (Atmospheric) has a 30% chance to fail in the demo to show off the 'Savings Ticker'
        passed = True
        reason = "Passed"
        
        if name == "GATE_2_ATMOSPHERIC" and random.random() < 0.3:
            passed = False
            reason = "Cloud Spike Detected (78.3% coverage)"

        return {
            "gate": name,
            "passed": passed,
            "reason": reason,
            "status": "COMPLETE"
        }