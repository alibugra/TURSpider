# !pip install -q accelerate==0.27.2 peft==0.4.0 bitsandbytes==0.40.2 transformers==4.38.2 trl==0.4.7
# !pip install --upgrade git+https://github.com/huggingface/transformers

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import LoraConfig, PeftModel
from trl import SFTTrainer

from huggingface_hub import notebook_login
notebook_login()

from google.colab import drive
drive.mount('/content/drive/')

model_name = "TURKCELL/Turkcell-LLM-7b-v1"

# Fine-tuned model name
new_model = "turkcell-llm-test"

# LoRA attention dimension
lora_r = 64

# Alpha parameter for LoRA scaling
lora_alpha = 16

# Dropout probability for LoRA layers
lora_dropout = 0.1

# Activate 4-bit precision base model loading
use_4bit = True

# Compute dtype for 4-bit base models
bnb_4bit_compute_dtype = "float16"

# Quantization type (fp4 or nf4)
bnb_4bit_quant_type = "nf4"

# Activate nested quantization for 4-bit base models (double quantization)
use_nested_quant = False

# Output directory where the model predictions and checkpoints will be stored
output_dir = "./results"

# Number of training epochs
num_train_epochs = 1

# Enable fp16/bf16 training (set bf16 to True with an A100)
fp16 = False
bf16 = False

# Batch size per GPU for training
per_device_train_batch_size = 4

# Batch size per GPU for evaluation
per_device_eval_batch_size = 4

# Number of update steps to accumulate the gradients for
gradient_accumulation_steps = 1

# Enable gradient checkpointing
gradient_checkpointing = True

# Maximum gradient normal (gradient clipping)
max_grad_norm = 0.3

# Initial learning rate (AdamW optimizer)
learning_rate = 2e-4

# Weight decay to apply to all layers except bias/LayerNorm weights
weight_decay = 0.001

# Optimizer to use
optim = "paged_adamw_32bit"

# Learning rate schedule
lr_scheduler_type = "cosine"

# Number of training steps (overrides num_train_epochs)
max_steps = -1

# Ratio of steps for a linear warmup (from 0 to learning rate)
warmup_ratio = 0.03

# Group sequences into batches with same length
# Saves memory and speeds up training considerably
group_by_length = True

# Save checkpoint every X updates steps
save_steps = 0

# Log every X updates steps
logging_steps = 25

# Maximum sequence length to use
max_seq_length = None

# Pack multiple short examples in the same input sequence to increase efficiency
packing = False

# Load the entire model on the GPU 0
device_map = {"": 0}

my_dataset = load_dataset('text', data_files='/content/drive/My Drive/TURSpider/turspider_train.txt', split='train')
print(my_dataset)
print(my_dataset[0])
print(my_dataset[1])

# Load tokenizer and model with QLoRA configuration
compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=use_4bit,
    bnb_4bit_quant_type=bnb_4bit_quant_type,
    bnb_4bit_compute_dtype=compute_dtype,
    bnb_4bit_use_double_quant=use_nested_quant,
)

# Check GPU compatibility with bfloat16
if compute_dtype == torch.float16 and use_4bit:
    major, _ = torch.cuda.get_device_capability()
    if major >= 8:
        print("=" * 80)
        print("Your GPU supports bfloat16: accelerate training with bf16=True")
        print("=" * 80)

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map=device_map,
    use_auth_token=True
)
model.config.use_cache = False
model.config.pretraining_tp = 1

# Load LLaMA tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right" # Fix weird overflow issue with fp16 training

# Load LoRA configuration
peft_config = LoraConfig(
    lora_alpha=lora_alpha,
    lora_dropout=lora_dropout,
    r=lora_r,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj","gate_proj"] # only Mistral
)

# Set training parameters
training_arguments = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=num_train_epochs,
    per_device_train_batch_size=per_device_train_batch_size,
    gradient_accumulation_steps=gradient_accumulation_steps,
    optim=optim,
    save_steps=save_steps,
    logging_steps=logging_steps,
    learning_rate=learning_rate,
    weight_decay=weight_decay,
    fp16=fp16,
    bf16=bf16,
    max_grad_norm=max_grad_norm,
    max_steps=max_steps,
    warmup_ratio=warmup_ratio,
    group_by_length=group_by_length,
    lr_scheduler_type=lr_scheduler_type,
    report_to="tensorboard",
    seed=123
)

# Set supervised fine-tuning parameters
trainer = SFTTrainer(
    model=model,
    train_dataset=my_dataset,
    peft_config=peft_config,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    args=training_arguments,
    packing=packing,
)

# Train model
trainer.train()

# Save trained model
trainer.model.save_pretrained(new_model)

try:
  trainer.model.save_pretrained("/content/drive/My Drive/TURSpider/" + new_model)
except:
  pass
  
# Ignore warnings
logging.set_verbosity(logging.CRITICAL)

import re

torch.cuda.empty_cache()

lines = []
output_file = open("/content/drive/My Drive/TURSpider/output/turspider_turkcell_output.txt", "w")

with open('/content/drive/My Drive/TURSpider/turspider_dev.txt', 'r', encoding='utf-8') as file:
    count = 0
    for line in file:
        count = count + 1
        print(count)

        try:
          prompt = line.strip()

          prompt = "<s>[INST] " + prompt + "[/INST]"

          max_new_tokens = 256

          inputs = tokenizer.encode(prompt, return_tensors="pt").to("cuda")
          outputs = model.generate(inputs, max_new_tokens=int(max_new_tokens))
          input_text = tokenizer.decode(outputs[0])

          regex_pattern = r'\[/INST\](.*)'
          matched = re.search(regex_pattern, input_text)
          generated_text = ""
          if matched:
            generated_text = matched.group(1).strip().split(';')[0].strip()

          print(generated_text)

          lines.append(generated_text + '\n')

          if generated_text == " " or generated_text == "":
            with open('/content/drive/My Drive/TURSpider/llm_output' + str(count) + '.txt', 'w') as f:
              f.write(input_text)
        except:
          try:
            with open('/content/drive/My Drive/TURSpider/llm_output' + str(count) + '.txt', 'w') as f:
              f.write(input_text)
          except:
            pass

output_file.writelines(lines)
output_file.close()
