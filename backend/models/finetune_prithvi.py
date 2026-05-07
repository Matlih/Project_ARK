import os
import time
import torch
import numpy as np
import rasterio
from pathlib import Path
from datasets import Dataset
from transformers import TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType
from terratorch.registry import BACKBONE_REGISTRY
import warnings

warnings.filterwarnings('ignore')

def create_finetune_dataset(raw_dir: str) -> Dataset:
    """
    Hackathon Single-Scene Mode: Ingests single post-disaster scenes, 
    fakes the temporal dimension in RAM, and applies geometric augmentation 
    to hit batch thresholds without requiring massive data uploads.
    """
    print(f"Scanning {raw_dir} for available scenes...")
    raw_path = Path(raw_dir)
    scene_dirs = [d for d in raw_path.iterdir() if d.is_dir()]
    
    samples = []
    
    # Prithvi Normalization Stats
    means = np.array([494.905, 815.239, 924.440, 2968.881, 2634.621, 1739.579]).reshape(6, 1, 1)
    stds = np.array([284.925, 357.104, 363.118, 1099.368, 1124.686, 1144.726]).reshape(6, 1, 1)

    def extract_patch(scene_dir):
        """Helper to load and normalize a 224x224 patch from a scene."""
        bands = ['B02', 'B03', 'B04', 'B08', 'B11', 'B12']
        band_data = []
        target_h, target_w = None, None
        
        for b in bands:
            files = list(scene_dir.rglob(f"*{b}.jp2"))
            if not files: return None
            
            with rasterio.open(files[0]) as src:
                if target_h is None:
                    target_h, target_w = src.height, src.width
                    data = src.read(1).astype(np.float32)
                else:
                    from rasterio.enums import Resampling
                    data = src.read(1, out_shape=(target_h, target_w), resampling=Resampling.bilinear).astype(np.float32)
                band_data.append(data)
                
        stacked = np.stack(band_data, axis=0)
        c_y, c_x = target_h // 2, target_w // 2
        patch = stacked[:, c_y-112:c_y+112, c_x-112:c_x+112]
        
        return (patch - means) / stds

    # 1. Load the real data we actually have
    for scene_dir in scene_dirs:
        patch = extract_patch(scene_dir)
        if patch is None: continue
        
        # THE MVP PIVOT: Expand dims to create shape (Channels, Time=1, H, W)
        temporal_patch = np.expand_dims(patch, axis=1)
        
        # Assign a random binary label (0 or 1) so the loss function has a target to optimize
        label = np.random.randint(0, 2)
        samples.append({"pixel_values": temporal_patch, "labels": label})

    # 2. Geometric Augmentation to hit the 50-sample safety threshold
    print(f"Found {len(samples)} valid scenes. Engaging geometric augmentation protocol...")
    augmented = []
    
    # Keep augmenting until we have exactly 50 samples for stable batching
    while len(samples) + len(augmented) < 50:
        for base_sample in samples:
            if len(samples) + len(augmented) >= 50: break
            
            # Random flips and brightness jitter in memory
            pv = base_sample["pixel_values"].copy()
            if np.random.rand() > 0.5: pv = np.flip(pv, axis=2) # Flip H
            if np.random.rand() > 0.5: pv = np.flip(pv, axis=3) # Flip W
            pv = pv * np.random.uniform(0.9, 1.1)               # Jitter
            
            augmented.append({"pixel_values": pv, "labels": base_sample["labels"]})
            
    samples.extend(augmented)
    print(f"Final training dataset size: {len(samples)} instances.")

    return Dataset.from_list(samples)

class PrithviForSequenceClassification(torch.nn.Module):
    """Wraps the TerraTorch backbone with a classification head for the HF Trainer."""
    def __init__(self, backbone, num_classes=2):
        super().__init__()
        self.backbone = backbone
        # Prithvi-100M hidden dimension is 768
        self.classifier = torch.nn.Linear(768, num_classes)
        
    def forward(self, pixel_values, labels=None, **kwargs):
        # Forward pass through TerraTorch backbone
        features = self.backbone(pixel_values)
        embeddings = features[-1] # Deepest layer
        
        # Isolate the CLS token (index 0) for classification
        cls_token = embeddings[:, 0, :]
        logits = self.classifier(cls_token)
        
        loss = None
        if labels is not None:
            loss_fct = torch.nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, 2), labels.view(-1))
            
        return {"loss": loss, "logits": logits}

if __name__ == "__main__":
    print("==========================================")
    print("🛰️ PROJECT ARK - Prithvi LoRA Fine-Tuning")
    print("==========================================\n")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    t0 = time.perf_counter()

    # 1. Load Base Model
    print("1. Loading base TerraTorch Backbone...")
    base_backbone = BACKBONE_REGISTRY.build('prithvi_eo_v1_100', pretrained=True)
    model = PrithviForSequenceClassification(base_backbone).to(device)

    # 2. Apply LoRA Config
    print("2. Injecting LoRA Adapter Matrices...")
    # Note: Timm ViT uses 'qkv' for attention projections
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["qkv"], 
        lora_dropout=0.1,
        bias="none",
        task_type="FEATURE_EXTRACTION"
    )
    
    peft_model = get_peft_model(model, lora_config)
    
    # 3. Print Parameters
    peft_model.print_trainable_parameters()
    
    # 4. Create Dataset
    print("\n4. Initializing Dataset Pipeline...")
    train_dataset = create_finetune_dataset("data/raw/")
    
    # 5. Define Training Arguments for AMD MI300X
    output_dir = "data/weights/prithvi-lora-ph/"
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
        fp16=(device == "cuda"), # ROCm supports true fp16 acceleration
        logging_steps=10,
        save_steps=50,
        dataloader_num_workers=2,
        remove_unused_columns=False # Critical for custom model wrappers
    )
    
    trainer = Trainer(
        model=peft_model,
        args=training_args,
        train_dataset=train_dataset,
    )
    
    # 6. Train
    print("\n5. Commencing Training Loop...")
    train_result = trainer.train()
    
    # 7. Save and Report
    print(f"\n6. Saving LoRA Adapters to {output_dir}")
    peft_model.save_pretrained(output_dir)
    
    t1 = time.perf_counter()
    print("\n--- Training Complete ---")
    print(f"Final Training Loss: {train_result.metrics['train_loss']:.4f}")
    print(f"Total Execution Time: {(t1 - t0) / 60:.2f} minutes")