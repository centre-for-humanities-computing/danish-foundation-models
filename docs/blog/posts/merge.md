---
draft: false
date: 2024-02-02
---


# Tutorial: Merging Language Models

Model merging is a relatively new method that allows one to combine the weights of different language models into a single model.

In this notebook you'll get to try this out, as well as try to interact with the merged model to see the results!

<!-- more -->

The [mergekit README](https://github.com/cg123/mergekit) is good to have open for this notebook. 
It has descriptions and examples for the different merge methods it supports.

## Install Dependencies


```python
# Uncomment to install packages (already done for you)
# !git clone https://github.com/cg123/mergekit.git
# %cd mergekit
# %pip install -e .
# %cd ..
```


```python
# General packages
import torch
import shutil
from pathlib import Path

# For merging the models
from mergekit.config import MergeConfiguration
from mergekit.merge import MergeOptions, run_merge

# For loading the models and running them after the merge
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer, GenerationConfig
```

## Get Hugging Face Token

To allow merging gated models (like LLaMA-2) and to upload your merged models, you can put your Hugging Face token in the cell below.

You can generate a token at https://hf.co/settings/tokens.

If you don't want to supply a token then simply leave it blank!


```python
import getpass
HUGGING_FACE_TOKEN = getpass.getpass("Hugging Face Token: ")
if not HUGGING_FACE_TOKEN:
    print("Not using a Hugging Face token.")
    HUGGING_FACE_TOKEN = None
```

## Configure the Merge

This is where we set up which models we would like to merge, and which merging method to use.

This configuration was the configuration used to create the Munin-NeuralBeagle model, but you can change it to whatever you like!


```python
merge_config = dict(
    models=[
        dict(
            model="danish-foundation-models/munin-7b-alpha",
        ),
        dict(
            model="mlabonne/NeuralBeagle14-7B",
            parameters=dict(
                density=0.53,
                weight=0.6,
            ),
        ),
    ],
    merge_method="dare_ties",
    base_model="danish-foundation-models/munin-7b-alpha",
    parameters=dict(
        int8_mask=True,
    ),
    dtype="bfloat16",
)
```


```python
LAZY_UNPICKLE = False  # Experimental low-memory model loader
LOW_CPU_MEMORY = True  # Enable if you have more VRAM than RAM+swap
OUT_PATH = "./merged"
```

## Merge!


```python
run_merge(
    MergeConfiguration.model_validate(merge_config),
    out_path=OUT_PATH,
    options=MergeOptions(
        lora_merge_cache="/tmp",
        cuda=torch.cuda.is_available(),
        copy_tokenizer=True,
        lazy_unpickle=LAZY_UNPICKLE,
        low_cpu_memory=LOW_CPU_MEMORY,
    )
)
```

## Try it Out

Time to try out the new merged model. Let's start by loading it from disk.


```python
model = AutoModelForCausalLM.from_pretrained(OUT_PATH, load_in_4bit=True)
tokenizer = AutoTokenizer.from_pretrained(OUT_PATH)

# Choosing a chat template for a merged model can be difficult. The one defined in 
# NeuralBeagle seems broken. Additionally, it does not have special tokens that some 
# of the merged models might have been trained with
tokenizer.chat_template = """
{% if not add_generation_prompt is defined %}
    {% set add_generation_prompt = false %}
{% endif %}
{% for message in messages %}
    {{'<|im_start|>' + message['role'] + '\n' + message['content'] + '<|im_end|>' + '\n'}}
{% endfor %}
{% if add_generation_prompt %}
    {{ '<|im_start|>assistant\n' }}
{% endif %}
"""

pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="auto",
)
```

Next, we need to set up how to generate text with it. You can leave the following config as-is, or you can experiment. [Here](https://huggingface.co/docs/transformers/v4.37.2/en/main_classes/text_generation#transformers.GenerationConfig) is a list of all the different arguments.


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
    pad_token_id=tokenizer.eos_token_id
)
```


```python
messages = [
    dict(
        role="system",
        content=""  # Change this to anything you want
    ),
    dict(
        role="user",
        content="Hvad er en stor sprogmodel?"  # And change this too
    ),
]

outputs = pipeline(
    tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True), 
    streamer=TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True),
    generation_config=GENERATION_CONFIG,
)
```

## Share the Model

You can share your new model to the Hugging Face Hub - this requires that you've included your Hugging Face token at the top of this notebook.


```python
# model.push_to_hub("your_name/merged_model", token=HUGGING_FACE_TOKEN)
```

## Clean Up

This deletes the merged model, as well as clearing the Hugging Face cache.

**WARNING**: You will have to redownload any used models if you do this!


```python
# shutil.rmtree(OUT_PATH, ignore_errors=True)
# shutil.rmtree('/home/ubuntu/.cache', ignore_errors=True)
```
