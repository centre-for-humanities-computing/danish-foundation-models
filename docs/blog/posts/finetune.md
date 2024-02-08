---
draft: false
date: 2024-02-02
---


# Tutorial: Finetuning Language Models

This notebook will allow you to try out finetuning of the `munin-7b-alpha` model or, indeed, any other generative model out there.

We'll be finetuning the model on a Danish translated instruction tuning dataset, using the QLoRA method.

<!-- more -->

## Install Dependencies


```python
# Uncomment to install packages (already done for you)
# %pip install --upgrade --force-reinstall --no-cache-dir torch==2.1.1 triton --index-url https://download.pytorch.org/whl/cu121
# %pip install "unsloth[cu121_ampere_torch211] @ git+https://github.com/unslothai/unsloth.git"
```


```python
# General packages
import torch
import getpass

# For loading the finetuning datasets
from datasets import load_dataset

# For loading and finetuning the models
from unsloth import FastLanguageModel
from trl import SFTTrainer, setup_chat_format
from transformers import TrainingArguments, AutoTokenizer, TextStreamer, GenerationConfig
```

## Get Hugging Face Token

To allow finetuning gated models (like LLaMA-2) and to upload your finetuned models, you can put your Hugging Face token in the cell below.

You can generate a token at https://hf.co/settings/tokens.

If you don't want to supply a token then simply leave it blank!


```python
HUGGING_FACE_TOKEN = getpass.getpass("Hugging Face Token: ")
if not HUGGING_FACE_TOKEN:
    print("Not using a Hugging Face token.")
    HUGGING_FACE_TOKEN = None
```

## Configure the Model


```python
RANDOM_SEED = 42

MODEL_CONFIGURATION = dict(
    model_name="danish-foundation-models/munin-7b-alpha",
    max_seq_length=2048,  
    dtype=None,  # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+ GPUs
    load_in_4bit=True,  # Use 4bit quantisation to reduce memory usage. Quantises on the fly, so can take a while.
    attn_implementation="flash_attention_2"
)

PEFT_CONFIGURATION = dict(
    r = 16,  # Adapter rank, choose any number > 0, but suggested 8, 16, 32, 64, 128
    target_modules=[
        "q_proj", 
        "k_proj", 
        "v_proj", 
        "o_proj", 
        "gate_proj", 
        "up_proj", 
        "down_proj",
    ],
    lora_alpha = 16,
    lora_dropout = 0,  # Supports any, but = 0 is optimized
    bias = "none",  # Supports any, but = "none" is optimized
    use_gradient_checkpointing = True,
    use_rslora = False,  # Support rank stabilized LoRA
    loftq_config = None,  # And LoftQ
    random_state = RANDOM_SEED,
)

FINETUNING_CONFIGURATION = dict(
    per_device_train_batch_size=8,
    gradient_accumulation_steps=1,
    warmup_steps=5,
    num_train_epochs=1,
    learning_rate=2e-4,
    weight_decay=0.01,
    lr_scheduler_type="linear",
)
```

## Load the Model


```python
model, tokenizer = FastLanguageModel.from_pretrained(**MODEL_CONFIGURATION, token=HUGGING_FACE_TOKEN)
model, tokenizer = setup_chat_format(model=model, tokenizer=tokenizer)
model = FastLanguageModel.get_peft_model(model, **PEFT_CONFIGURATION)
```

## Load and Prepare Data

Load the dataset from Hugging Face Hub:


```python
dataset = load_dataset("kobprof/skolegpt-instruct", split="train")
print(f"Number of samples in dataset: {len(dataset):,}")
```

We just take a random subset, 1000 samples should take around 7 minutes on this machine depending on settings.


```python
n_samples = 1000
dataset = dataset.shuffle(seed=RANDOM_SEED).select(range(n_samples))
```

Lastly, we set up the conversations in the dataset into the standard ChatML format.


```python
def create_conversation(sample: dict) -> dict[str, list[dict[str, str]]]:
    """This converts the sample to the standardised ChatML format.

    Args:
        sample:
            The data sample.

    Returns:
        The sample set up in the ChatML format.
    """
    return {
        "messages": [
            {"role": "system", "content": sample["system_prompt"]},
            {"role": "user", "content": sample["question"]},
            {"role": "assistant", "content": sample["response"]}
        ]
    }

dataset = dataset.map(create_conversation, batched=False)
```

## Finetune!


```python
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    max_seq_length=MODEL_CONFIGURATION["max_seq_length"],
    dataset_num_proc=4,
    packing=True,  # Can make training 5x faster for short sequences.
    args = TrainingArguments(
        optim="adamw_8bit",
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=3,
        seed=RANDOM_SEED,
        output_dir="outputs",
        **FINETUNING_CONFIGURATION
    ),
)
```


```python
# Log some GPU stats before we start the finetuning
gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(
    f"You're using the {gpu_stats.name} GPU, which has {max_memory:.2f} GB of memory "
    f"in total, of which {start_gpu_memory:.2f}GB has been reserved already."
)
```


```python
# This is where the actual finetuning is happening
trainer_stats = trainer.train()
```


```python
# Log some post-training GPU statistics
used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
used_percentage = round(used_memory / max_memory * 100, 3)
lora_percentage = round(used_memory_for_lora / max_memory * 100, 3)
print(
    f"We ended up using {used_memory:.2f} GB GPU memory ({used_percentage:.2f}%), "
    f"of which {used_memory_for_lora:.2f} GB ({lora_percentage:.2f}%) "
    "was used for LoRa."
)
```

## Try it Out

Time to try out the new finetuned model. First we need to set up how to generate text with it.

You can leave the following config as-is, or you can experiment. [Here](https://huggingface.co/docs/transformers/v4.37.2/en/main_classes/text_generation#transformers.GenerationConfig) is a list of all the different arguments.


```python
GENERATION_CONFIG = GenerationConfig(
    # What should be outputted
    max_new_tokens=256, 

    # Controlling how the model chooses the next token to generate
    do_sample=True, 
    temperature=0.2, 
    repetition_penalty=1.2,
    top_k=50,
    top_p=0.95,

    # Miscellaneous required settings
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.eos_token_id,
    use_cache=False,  # Required by unsloth
)
```

 Let's use `TextStreamer` for continuous inference - so you can see the generation token by token, instead of waiting the whole time!



```python
messages = [
    dict(
        role="system",
        content=""  # Change this to anything you want
    ),
    dict(
        role="user",
        content="Hvad synes du om Danish Foundation Models projektet? Skriv kortfattet."  # And change this too
    ),
]

outputs = model.generate(
    input_ids=tokenizer.apply_chat_template(chat, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda"),
    streamer=TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True),
    generation_config=GENERATION_CONFIG,
)
```

## Share the Model

You can share your new model to the Hugging Face Hub - this requires that you've included your Hugging Face token at the top of this notebook.


```python
# model.push_to_hub("your_name/qlora_model", token=HUGGING_FACE_TOKEN)
```

## Extra: Export Model to Other Frameworks

### Saving to float16 for vLLM

The popular inference framework [vLLM](https://docs.vllm.ai/en/latest/index.html) can take advantage of having a model available in lower precision, enabling faster inference times.

You can uncomment the following lines if you want to save the model in 16-bit or even 4-bit precision:


```python
# Merge to 16bit
# model.save_pretrained_merged("model", tokenizer, save_method="merged_16bit",)
# model.push_to_hub_merged("hf/model", tokenizer, save_method="merged_16bit", token=HUGGING_FACE_TOKEN)

# Merge to 4bit
# model.save_pretrained_merged("model", tokenizer, save_method="merged_4bit",)
# model.push_to_hub_merged("hf/model", tokenizer, save_method="merged_4bit", token=HUGGING_FACE_TOKEN)
```

Alternatively, you can save only the adapter weights, which are very light, but which requires the base model to be able to use it:


```python
# Just LoRA adapters
# model.save_pretrained_merged("model", tokenizer, save_method="lora",)
# model.push_to_hub_merged("hf/model", tokenizer, save_method="lora", token=HUGGING_FACE_TOKEN)
```

### GGUF / llama.cpp Conversion

You can also save the model in the popular `GGUF` or `llama.cpp` formats, by uncommenting any of the following:


```python
# Save to 8bit Q8_0
# model.save_pretrained_gguf("model", tokenizer)
# model.push_to_hub_gguf("hf/model", tokenizer, token=HUGGING_FACE_TOKEN)

# Save to 16bit GGUF
# model.save_pretrained_gguf("model", tokenizer, quantization_method="f16")
# model.push_to_hub_gguf("hf/model", tokenizer, quantization_method="f16", token=HUGGING_FACE_TOKEN)

# Save to q4_k_m GGUF
# model.save_pretrained_gguf("model", tokenizer, quantization_method="q4_k_m")
# model.push_to_hub_gguf("hf/model", tokenizer, quantization_method="q4_k_m", token=HUGGING_FACE_TOKEN)
```

Now, use the `model-unsloth.gguf` file or `model-unsloth-Q4_K_M.gguf` file in `llama.cpp` or a UI based system like `GPT4All`. You can install GPT4All by going [here](https://gpt4all.io/index.html).
