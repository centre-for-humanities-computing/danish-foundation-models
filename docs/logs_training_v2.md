# Logs from training version 2

- K. Enevoldsen (7-8 October, server: Grundtvig): Testing training using a small sample:

```bash
python src/applications/train/run_mlm_pytorch_stream.py \
    --dataset_name dcc_v1.1.0 \
    --model_name_or_path roberta-base \
    --output_dir /data-big-projects/danish-foundation-models/models \
    --max_steps 1 \
    --overwrite_output_dir \
    --do_train \
    --streaming \
    --max_train_samples 1000 \
    --do_eval
```


- K. Enevoldsen (8 October, server: Grundtvig): Started training using same parameters as [dfm-bert-base](https://wandb.ai/kenevoldsen/danish_foundation_models/runs/2q8odc6w/overview?workspace=user-kenevoldsen), with the notable exception of using a 16 bit floats (to allow for the same batch size despite running on smaller GPUs). The previous script was trained using FLAX and can be found [here](https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/40d9e3404c42169470c08dc8b98d197163bd779a/src/applications/train/run_mlm_flax_stream.py).

```
cd /data-big-projects/danish-foundation-models/
git clone https://huggingface.co/chcaa/dfm-bert-base-v1
```
 
```bash
python src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/data-big-projects/danish-foundation-models/models \
    --tokenizer_name=/data-big-projects/danish-foundation-models/dfm-bert-base-v1 \
    --model_type=bert \
    --config_name=/data-big-projects/danish-foundation-models/dfm-bert-base-v1 \
    --dataset_name=dcc_v1.1.0 \
    --max_seq_length=512 \
    --per_device_train_batch_size=48 \
    --per_device_eval_batch_size=48 \
    --learning_rate=2e-5 \
    --warmup_steps=10000 \
    --adam_beta1=0.9 \
    --adam_beta2=0.999 \
    --max_steps=1500000 \
    --max_eval_samples=5000 \
    --logging_steps=500 \
    --eval_steps=10000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --do_eval \
    --do_train \
    --streaming \
    --seed=42 \
    --overwrite_output_dir \
    --fp16 \
    --nat_weight=0.50 \
    --danews_weight=0.20 \
    --hopetwittet_weight=0.20 \
    --dagw_dfm_weight=0.10 


```


python src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/data-big-projects/danish-foundation-models/models \
    --tokenizer_name=/data-big-projects/danish-foundation-models/dfm-bert-base-v1 \
    --model_type=bert \
    --config_name=/data-big-projects/danish-foundation-models/dfm-bert-base-v1 \
    --dataset_name=dcc_v1.1.0 \
    --max_seq_length=512 \
    --per_device_train_batch_size=2 \
    --per_device_eval_batch_size=2 \
    --learning_rate=2e-5 \
    --warmup_steps=10000 \
    --adam_beta1=0.9 \
    --adam_beta2=0.999 \
    --max_steps=1500000 \
    --max_eval_samples=5000 \
    --logging_steps=500 \
    --eval_steps=10000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --do_eval \
    --do_train \
    --streaming \
    --seed=42 \
    --fp16


Checked:
- [x] check that it runs with a bert
- [x] does our grundtvig support bf16? (No it does not)
- [x] train custom tokenizer
- [x] train with a custom bert
- [x] set up the slack integration (should be DDSC)
- [x] set up wandb integration (should be DSCC or CHCAA)
- [x] fix such that training can restart from a given point (given point in the dataset as well)
