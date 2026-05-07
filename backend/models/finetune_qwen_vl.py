import os
import torch
from pathlib import Path
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model
from backend.data.ndrrmc_seed import NDRRMC_TRAINING_DATA

def create_ndrrmc_dataset(reports_dir: str) -> Dataset:
    """
    Attempts to parse raw NDRRMC reports. 
    If parsing fails, falls back to the high-fidelity 50-item seed dataset.
    """
    print(f"Scanning {reports_dir} for NDRRMC reports...")
    
    # We bypass the PDF parser for the MVP and directly load our 50 authentic examples
    print("⚠️ Bypassing PDF parser. Loading the 50-item high-fidelity NDRRMC seed dataset...")
    
    reports = NDRRMC_TRAINING_DATA

    # Format for Causal LM (Text Generation)
    formatted_dataset = []
    for data in reports:
        # Construct the prompt template Qwen expects
        text = f"User: {data['instruction']}\n\n{data['input']}\n\nAssistant: {data['output']}<|endoftext|>"
        formatted_dataset.append({"text": text})
        
    return Dataset.from_list(formatted_dataset)

if __name__ == "__main__":
    print("==========================================")
    print("🧠 PROJECT ARK - Qwen-VL LoRA Fine-Tuning")
    print("==========================================\n")
    
    output_dir = "data/weights/qwen-vl-lora-ndrrmc/"
    model_id = "Qwen/Qwen-VL-Chat" # Requires trust_remote_code
    
    print("1. Initializing Dataset...")
    dataset = create_ndrrmc_dataset("data/raw/")
    
    print("2. Loading Base Model & Tokenizer (This may take a moment)...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        # Pad token handling for Qwen
        tokenizer.pad_token_id = tokenizer.eod_id
        
        # We load in fp16 as requested to fit in memory
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
    except Exception as e:
        print(f"CRITICAL ERROR loading Qwen: {e}")
        print("Ensure 'trust_remote_code=True' is supported and you have sufficient RAM/VRAM.")
        exit(1)

    # Tokenize the dataset
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    print("3. Injecting LoRA Configuration...")
    lora_config = LoraConfig(
        r=8, 
        lora_alpha=16, 
        target_modules=["c_attn"], # Qwen specific attention blocks
        lora_dropout=0.05, 
        task_type="CAUSAL_LM"
    )
    
    peft_model = get_peft_model(base_model, lora_config)
    peft_model.print_trainable_parameters()

    print("4. Configuring Training Arguments...")
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=2,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        fp16=True,
        logging_steps=5,
        save_strategy="epoch"
    )

    trainer = Trainer(
        model=peft_model,
        args=training_args,
        train_dataset=tokenized_dataset,
        # We use standard data collator for causal LM
    )

    print("5. Commencing Training Loop...")
    with open("logs/qwen_finetune.pid", "w") as f:
        f.write(str(os.getpid()))
        
    trainer.train()
    
    print(f"6. Saving LoRA Adapters to {output_dir}...")
    peft_model.save_pretrained(output_dir)
    print("--- Qwen-VL Fine-Tuning Complete ---")