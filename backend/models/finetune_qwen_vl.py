import os
import torch
from pathlib import Path
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model
from backend.data.ndrrmc_seed import NDRRMC_TRAINING_DATA

# Force internal library to recognize ROCm environment if bitsandbytes is finicky
os.environ["BNB_CUDA_VERSION"] = "121" # Dummy for bitsandbytes fallback
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "9.4.2"

def create_ndrrmc_dataset() -> Dataset:
    """Loads the 50-item high-fidelity NDRRMC seed dataset."""
    print("🧠 Loading the 50-item high-fidelity NDRRMC seed dataset...")
    
    formatted_dataset = []
    for data in NDRRMC_TRAINING_DATA:
        # Construct the prompt template Qwen expects
        text = f"User: {data['instruction']}\n\n{data['input']}\n\nAssistant: {data['output']}<|endoftext|>"
        formatted_dataset.append({"text": text})
        
    return Dataset.from_list(formatted_dataset)

if __name__ == "__main__":
    print("==========================================")
    print("🧠 PROJECT ARK - Qwen-VL LoRA Fine-Tuning")
    print("==========================================\n")
    
    output_dir = "data/weights/qwen-vl-lora-ndrrmc/"
    model_id = "Qwen/Qwen-VL-Chat"
    
    # 1. Initialize Dataset
    dataset = create_ndrrmc_dataset()
    
    # 2. Load Tokenizer & Model
    print("2. Loading Base Model & Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    tokenizer.pad_token_id = tokenizer.eod_id
    
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    # 3. Tokenize with Labels (Fix for the ValueError)
    def tokenize_function(examples):
        tokenized_output = tokenizer(
            examples["text"], 
            padding="max_length", 
            truncation=True, 
            max_length=512
        )
        # For CausalLM, labels are the input_ids
        tokenized_output["labels"] = [list(ids) for ids in tokenized_output["input_ids"]]
        return tokenized_output

    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

    # 4. Inject LoRA
    print("3. Injecting LoRA Configuration...")
    lora_config = LoraConfig(
        r=8, 
        lora_alpha=16, 
        target_modules=["c_attn"], 
        lora_dropout=0.05, 
        task_type="CAUSAL_LM"
    )
    
    peft_model = get_peft_model(base_model, lora_config)
    peft_model.print_trainable_parameters()

    # 5. Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=5, # Increased slightly for 50 examples
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        fp16=True,
        logging_steps=1,
        save_strategy="no", # We save manually at the end
        learning_rate=2e-4,
        weight_decay=0.01,
        push_to_hub=False,
        report_to="none"
    )

    # Use a data collator that understands language modeling
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=peft_model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    print("5. Commencing Training Loop...")
    # Save PID for monitoring
    with open("logs/qwen_finetune.pid", "w") as f:
        f.write(str(os.getpid()))
        
    trainer.train()
    
    # 6. Save final adapter
    print(f"6. Saving LoRA Adapters to {output_dir}...")
    peft_model.save_pretrained(output_dir)
    print("--- Qwen-VL Fine-Tuning Complete ---")