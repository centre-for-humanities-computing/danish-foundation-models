
# Logs 

- may 26: After noble-dew-60 stops training Dan ran a subset of scandeval obtaining the scores;
```
dfm-bert:
    dane: 60.87 ± 2.08
    angry-tweets: 42.16 ± 1.65
    scala-da: 16.27 ± 5.49
```
- 29 may: starting conducting logs.
- 29 may: After having restarted it after faithful out experience that the process hangs, we switched to version 0.3.12 of JAX and reran the scripts. This reason for this switch is that previously GPUs ran without issues for multiple days.
    - Seems like the issue is caused by UCloud putting an app to sleep, sometimes reopening it starts the script again. I (KCE) have sent a ticket to UCloud. 
- 30 may: Script went to sleep again, using a TMUX instance did not resolve the issue. I (KCE) have reached out to Kristoffer, planning a meeting later today. Restarting training from aburd leaf 78 using;

```bash
python3 /work/danish-foundation-models/src/applications/train/run_mlm_flax_stream.py \
    --output_dir=/work/models/transformers/dfm-bert-base \
    --model_name_or_path=/work/models/transformers/dfm-bert-base \
    --config_name=/work/models/transformers/dfm-bert-base \
    --tokenizer_name=/work/models/transformers/dfm-bert-base \
    --dataset_name=dcc-v1 \
    --max_seq_length=512 \
    --per_device_train_batch_size=46 \
    --per_device_eval_batch_size=46 \
    --learning_rate=0.00001775 \
    --warmup_steps=1 \
    --overwrite_output_dir \
    --adam_beta1=0.9 \
    --adam_beta2=0.999 \
    --num_train_steps=1240000 \
    --num_eval_samples=5000 \
    --logging_steps=500 \
    --eval_steps=10000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --skip_n_training_docs=25984000 \
    --seed=6
```

- 31 may; ran a subset of scandeval obtained score:
```
Dane: 
↳ Micro-average F1-score:
  - Test: 67.15 ± 2.36
↳ Micro-average F1-score without MISC tags:
  - Test: 71.92 ± 2.80

tweet:
↳ Matthew's correlation coefficient:
  - Test: 44.38 ± 1.99

scala: 
↳ Matthew's correlation coefficient:
  - Test: 48.55 ± 10.20
```


- 31 may: Run polar-terrain crashed again, restarted using:

```bash
python3 /work/danish-foundation-models/src/applications/train/run_mlm_flax_stream.py \
    --output_dir=/work/models/transformers/dfm-bert-base \
    --model_name_or_path=/work/models/transformers/dfm-bert-base \
    --config_name=/work/models/transformers/dfm-bert-base \
    --tokenizer_name=/work/models/transformers/dfm-bert-base \
    --dataset_name=dcc-v1 \
    --max_seq_length=512 \
    --per_device_train_batch_size=46 \
    --per_device_eval_batch_size=46 \
    --learning_rate=0.00001565 \
    --warmup_steps=1 \
    --overwrite_output_dir \
    --adam_beta1=0.9 \
    --adam_beta2=0.999 \
    --num_train_steps=1240000 \
    --num_eval_samples=5000 \
    --logging_steps=500 \
    --eval_steps=10000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --skip_n_training_docs=51111000 \
    --seed=6
```
- 31 may: Run honest lake timed outz again, restarted using:
```bash
python3 /work/danish-foundation-models/src/applications/train/run_mlm_flax_stream.py \
    --output_dir=/work/models/transformers/dfm-bert-base \
    --model_name_or_path=/work/models/transformers/dfm-bert-base \
    --config_name=/work/models/transformers/dfm-bert-base \
    --tokenizer_name=/work/models/transformers/dfm-bert-base \
    --dataset_name=dcc-v1 \
    --max_seq_length=512 \
    --per_device_train_batch_size=46 \
    --per_device_eval_batch_size=46 \
    --learning_rate=0.00001542 \
    --warmup_steps=1 \
    --overwrite_output_dir \
    --adam_beta1=0.9 \
    --adam_beta2=0.999 \
    --num_train_steps=1240000 \
    --num_eval_samples=5000 \
    --logging_steps=500 \
    --eval_steps=10000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --skip_n_training_docs=52459000 \
    --seed=6
```

- 1 jun: Run skilled waterfall timed out again (this is not working), restarted using 4 V100 and a lower batch size
```bash
python3 /work/danish-foundation-models/src/applications/train/run_mlm_flax_stream.py \
    --output_dir=/work/models/transformers/dfm-bert-base \
    --model_name_or_path=/work/models/transformers/dfm-bert-base \
    --config_name=/work/models/transformers/dfm-bert-base \
    --tokenizer_name=/work/models/transformers/dfm-bert-base \
    --dataset_name=dcc-v1 \
    --max_seq_length=512 \
    --per_device_train_batch_size=32 \
    --per_device_eval_batch_size=32 \
    --learning_rate=0.00001530 \
    --warmup_steps=1 \
    --overwrite_output_dir \
    --adam_beta1=0.9 \
    --adam_beta2=0.999 \
    --num_train_steps=1240000 \
    --num_eval_samples=5000 \
    --logging_steps=500 \
    --eval_steps=10000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --skip_n_training_docs=54083000 \
    --seed=6
```

# How to train on UCloud

To setup to train in UCloud select the instance Coder CUDA v1.64.2 and install dependencies using:


```
pip install "jax[cuda11_cudnn82]" -f https://storage.googleapis.com/jax-releases/jax_releases.html
# impossible to specify in setup.cfg:
# see https://stackoverflow.com/questions/57689387/equivalent-for-find-links-in-setup-py

# install dfm
pip install -e .[ucloud_gpu]
```

Create model repository
```
huggingface-cli login
huggingface-cli repo create dfm-bert-base
```

Next we clone the model repository to add the tokenizer and model files.
```
cd  /work/models/transformers
git clone https://huggingface.co/<your-username>/dfm-bert-base
```

To ensure that all tensorboard traces will be uploaded correctly, we need to track them. You can run the following command inside your model repo to do so.
```
cd dfm-bert-base
git lfs track "*tfevents*"
cd ..
```
We will need to move the config from the DFM repository to the model repository:

```python
from transformers import BertTokenizerFast, BertConfig

model_dir = "./dfm-bert-base"

tokenizer = BertTokenizerFast.from_pretrained("Maltehb/danish-bert-botxo")
config = BertConfig.from_pretrained("Maltehb/danish-bert-botxo")

tokenizer.save_pretrained(model_dir)
config.save_pretrained(model_dir)
```

<!-- 
Using a custom config:
```
cp /work/danish-foundation-models/configs/debertav2-config_small.json ./dfm-debertav2-small/config.json
```
Similar for the tokenizer:
```
cp /work/models/tokenizers/dfm_tokenizer/unigram_5000000_docs_128000_tokens/tokenizer.json ./dfm-debertav2-small
```
-->
To allow for comparison we with the Danish BERT by botXO (now renamed Certainly.io). 
We try to keep as many training similar to the parameters of the original implementation.
With changes to batch size and maximum training sequence (to 512).
Where BotXO doesn't report its training parameters we use those of reported in the BERT paper.

<!--
Botxo BERT hyperparameters:
```
Batch size: 1280
Max predictions per training sentence: 20
Max training sentence length: 256
Probability of masking word in training sentence: 0.15
Learning rate: 2e-5
Training steps: 1.000.000
A custom BPE vocabulary of 32.000 tokens.
```
-->

```bash
python3 /work/danish-foundation-models/src/applications/train/run_mlm_flax_stream.py \
    --output_dir=/work/models/transformers/dfm-bert-base \
    --model_type=bert \
    --config_name=/work/models/transformers/dfm-bert-base \
    --tokenizer_name=/work/models/transformers/dfm-bert-base \
    --dataset_name=dcc-v1 \
    --max_seq_length=512 \
    --per_device_train_batch_size=48 \
    --per_device_eval_batch_size=48 \
    --learning_rate=2e-5 \
    --warmup_steps=10000 \
    --overwrite_output_dir \
    --adam_beta1=0.9 \
    --adam_beta2=0.999 \
    --num_train_steps=1500000 \
    --num_eval_samples=5000 \
    --logging_steps=500 \
    --eval_steps=10000 \
    --push_to_hub \
    --weight_decay=0.01
```
