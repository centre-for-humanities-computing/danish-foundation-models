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


- K. Enevoldsen (8-10 October, server: Grundtvig): Started training using same parameters as [dfm-bert-base](https://wandb.ai/kenevoldsen/danish_foundation_models/runs/2q8odc6w/overview?workspace=user-kenevoldsen), with the notable exception of using a 16 bit floats (to allow for the same batch size despite running on smaller GPUs). The previous script was trained using FLAX and can be found [here](https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/40d9e3404c42169470c08dc8b98d197163bd779a/src/applications/train/run_mlm_flax_stream.py).

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
    --do_train \
    --streaming \
    --seed=42 \
    --fp16 \
    --nat_weight=0.50 \
    --danews_weight=0.20 \
    --hopetwitter_weight=0.20 \
    --dagw_dfm_weight=0.10
    # --overwrite_output_dir \
```

- K. Enevoldsen (10 October, server: Grundtvig): This run did not seem to log evaluation scores. Stopping it to debug.
  
It seems like the cause was the lack of do_eval. The following should solve the issue, will restart it using this:

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
    --do_train \
    --streaming \
    --seed=42 \
    --fp16 \
    --do_eval \
    --evaluation_strategy="steps" \
    --nat_weight=0.50 \
    --danews_weight=0.20 \
    --hopetwitter_weight=0.20 \
    --dagw_dfm_weight=0.10
    # --overwrite_output_dir \
```

- K. Enevoldsen (10 October, server: Grundtvig): Parameters for next run:

**We will need to change**:
- logging frequency could probably be 1000 (see if this is related to GPU utilization, if not then 500 is fine)
- larger batch size

We discussed the following grid for small models:

> Updates on the small danish language models. After the above experiment is done the plan is to train a small-sized encoder to find the correct hyperparameters for larger models. This is the grid I propose we might want to search:
> 
> - dataset distributions (nat, twitter, news, dagw):
>   - [0.50. 0.20, 0.20. 0.10]
>   - [0.25. 0.25, 0.25. 0.25],
>   - [0.70, 0.10, 0.10, 0.10]
> - adjust learning rate (BERT is the only one which uses 1e-4 so this seems low, we use 2e-5 which is def. too low)
>   - [1e-4, 2e-4, 6e-4]
> - adam_epsilon (default is 1e-8, everyone else use 1e-6, probably not a big difference): 
>   - 1e-6
> - gradient clipping (probably better w. 0.1)
>   - [0.0, 0.1]
> - warm up steps (only roberta uses 24k for small models)
>   - [10k, 24k]
> - adam_beta2 (seems like most later paper uses 0.98 including roberta, electra, debertav3)
>   - [0.99, 0.98]
> - architectures (which we can currently train)
>   - RoBERTa, debertav2 
> - vocabulary size of tokenizer
>   - [32k, 50k, 128k]
> - tokenizer type (here wordpiece is probably better)
>   - [BPE, unigram]
> 
> For these hyperparameters I reviewed (deberta v1-3, electra, roberta and bert)
> 
> potentially we could reduce the search space, by assuming (some) of the following:
> tokenizer_type:unigram >= BPE
> adam_beta2: 0.98 >= 0.99
> gradient clipping: 0.1 >= 0.0
> learning_rate: [2e-4, 6e-4] >= 1e-4 # especially since we will use a larger batch size than BERT
> warm-up steps: 10k ~= 24k # approximately equal
> 
> Some other things we might try are:
> Changing activation function (e.g. this paper suggest geglu) 
> Similarly, try RMS Norm which also shows better performance for transformers (also used in gopher).
> We could also examine alternative positional embeddings (we kinda do this with the debertav2)

- K. Enevoldsen (11 October, server: Grundtvig): Stopping run.

This run did no seem to compare well with the previous flax implementation. In the message
on slack there might be some problems:

Troubles in model training paradise (seems like @Dan jinxed it :wink: ):

> Below we see the comparison between the old and the new run and it doesn’t seem great. I see three potential causes.
>
> - unlucky seed (it happens, we can’t guarantee the same order as the first training)
> - We use fp16 to match the batch size, it might have a hard time dealing with the very low learning rate
> - the HF trainer seems to default to gradient clipping (probably a good idea), but the flax script does not seem to use it (it is set in the training args, but it doesn’t seem to be used in the script - I this is not a mistake the training args is simply parsed by huggingface training args which might add unused arguments (this seems problematic but intensional) - gradient clipping combined with very low learning rate seems problematic (which might be why we don’t see the ‘tick’ down in loss similar to the first model)
> 
> There is naturally also that the dataset is worse (doesn’t seem to coincide with what we see) and or that there is some inherent PyTorch vs flax difference which causes it (that also doesn’t seem plausible)

Lasse and I decided to restart the run using a small BERT and drop the comparison w. existing models.

This requires:
- [x] retraining a tokenizer (32, 50, 128k vocab)
- [x] creating a config
- [ ] Setup autocreate and sync for a new HF repo (ready to be tested)
- [ ] setup on ucloud (ready to be tested)
  - [ ] needs HF login


```bash
python src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/data-big-projects/danish-foundation-models/huggingface-repositories/dfm-roberta-small-v1 \
    --tokenizer_name=/data-big-projects/danish-foundation-models/tokenizers/unigram_100000_docs_32000_vocab \
    --use_pretrained_tokenizer \
    --model_type=roberta \
    --config_name=/home/kenneth/github/danish-foundation-models/default-models-configs/small-roberta-config.json \
    --dataset_name=dcc_v1.1.0 \
    --max_seq_length=512 \
    --per_device_train_batch_size=48 \
    --per_device_eval_batch_size=48 \
    --learning_rate=2e-4 \
    --warmup_steps=10000 \
    --adam_beta1=0.9 \
    --adam_beta2=0.98 \
    --adam_epsilon=1e-6 \
    --max_steps=500000 \
    --max_eval_samples=5000 \
    --logging_steps=500 \
    --eval_steps=10000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --do_train \
    --streaming \
    --seed=42 \
    --fp16 \
    --do_eval \
    --evaluation_strategy=steps \
    --nat_weight=0.50 \
    --danews_weight=0.20 \
    --hopetwitter_weight=0.20 \
    --dagw_dfm_weight=0.10 \
    --overwrite_output_dir \
    --optim=adamw_torch
```
If you are wondering about optim, see [this](https://discuss.huggingface.co/t/huggingface-transformers-longformer-optimizer-warning-adamw/14711).

hmmm this did not seem to work initially. Will try changing one step at a time instead. 

- K. Enevoldsen (18 October, server: Grundtvig): Started run again
  
Seems like there was a problem with max sequence length being 512, instead it should be 514.
For related issues see:

- https://github.com/huggingface/transformers/issues/1363
- https://github.com/facebookresearch/fairseq/issues/1187


I then started the following run tuning the batch size:
```
python src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/data-big-projects/danish-foundation-models/huggingface-repositories/dfm-roberta-small-v1 \
    --tokenizer_name=/data-big-projects/danish-foundation-models/tokenizers/unigram_100000_docs_32000_vocab \
    --use_pretrained_tokenizer \
    --model_type=roberta \
    --config_name=/home/kenneth/github/danish-foundation-models/default-models-configs/small-roberta-config.json \
    --dataset_name=dcc_v1.1.0 \
    --max_seq_length=512 \
    --per_device_train_batch_size=256 \
    --per_device_eval_batch_size=128 \
    --learning_rate=2e-4 \
    --warmup_steps=1000 \
    --adam_beta1=0.9 \
    --adam_beta2=0.98 \
    --adam_epsilon=1e-6 \
    --max_steps=50000 \
    --max_eval_samples=5000 \
    --logging_steps=100 \
    --eval_steps=1000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --do_train \
    --streaming \
    --seed=42 \
    --fp16 \
    --do_eval \
    --evaluation_strategy=steps \
    --nat_weight=0.50 \
    --danews_weight=0.20 \
    --hopetwitter_weight=0.20 \
    --dagw_dfm_weight=0.10 \
    --overwrite_output_dir \
    --optim=adamw_torch
```


- K. Enevoldsen (19- October, server: Grundtvig): Start running the grid, we can do this in parallel on grundtvig be specifying `CUDA_VISIBLE_DEVICES=2 python train.py`

e.g.
```
CUDA_VISIBLE_DEVICES=0 python src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/data-big-projects/danish-foundation-models/huggingface-repositories/dfm-roberta-small-v1 \
    --tokenizer_name=/data-big-projects/danish-foundation-models/tokenizers/unigram_100000_docs_32000_vocab \
    --use_pretrained_tokenizer \
    --model_type=roberta \
    --config_name=/home/kenneth/github/danish-foundation-models/default-models-configs/small-roberta-config.json \
    --dataset_name=dcc_v1.1.0 \
    --max_seq_length=512 \
    --learning_rate=2e-4 \
    --warmup_steps=1000 \
    --adam_beta1=0.9 \
    --adam_beta2=0.98 \
    --adam_epsilon=1e-6 \
    --max_steps=50000 \
    --max_eval_samples=5000 \
    --logging_steps=100 \
    --eval_steps=1000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --do_train \
    --streaming \
    --seed=42 \
    --fp16 \
    --do_eval \
    --evaluation_strategy=steps \
    --nat_weight=0.50 \
    --danews_weight=0.20 \
    --hopetwitter_weight=0.20 \
    --dagw_dfm_weight=0.10 \
    --overwrite_output_dir \
    --per_device_train_batch_size=128 \
    --per_device_eval_batch_size=128 \
    --optim=adamw_torch
```

The results from the grid can be found [here](https://wandb.ai/chcaa/danish-foundation-models/reports/Grid-Search-1--VmlldzoyODE5NDE5).

- K. Enevoldsen (30- October, server: UCloud t4, run_names: [`run_mlm_train_01`, `run_mlm_train_01`]): Started running small-sized model and base sized model.

Following the hyperparameter search the following parameters seems reasonable.

```bash
python3 src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/home/ucloud/data/dfm-data/huggingface-repositories/dfm-debertav2-small-v1 \
    --tokenizer_name=/home/ucloud/data/dfm-data/tokenizers/unigram_100000_docs_32000_vocab \
    --model_type=deberta-v2 \
    --use_pretrained_tokenizer \
    --config_name=/home/ucloud/danish-foundation-models/default-models-configs/small-deberta-v2-32000-config.json \
    --dataset_name=dcc_v1.1.0 \
    --max_seq_length=512 \
    --learning_rate=6e-4 \
    --warmup_step=10000 \
    --adam_beta1=0.9 \
    --adam_beta2=0.98 \
    --adam_epsilon=1e-6 \
    --max_steps=100000 \
    --max_eval_samples=5000 \
    --logging_steps=100 \
    --eval_steps=2000 \
    --save_steps=2000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --do_train \
    --streaming \
    --seed=42 \
    --fp16 \
    --do_eval \
    --evaluation_strategy=steps \
    --nat_weight=0.60 \
    --danews_weight=0.20 \
    --hopetwitter_weight=0.10 \
    --dagw_dfm_weight=0.10 \
    --overwrite_output_dir \
    --per_device_train_batch_size=64 \
    --per_device_eval_batch_size=32 \
    --gradient_accumulation_steps=4 \
    --optim=adamw_torch
    # --overwrite_output_dir
```

and for the base-sized model:

```bash
python3 src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/home/ucloud/data/dfm-data/huggingface-repositories/dfm-debertav2-base-v1 \
    --tokenizer_name=/home/ucloud/data/dfm-data/tokenizers/unigram_100000_docs_32000_vocab \
    --model_type=deberta-v2 \
    --use_pretrained_tokenizer \
    --config_name=/home/ucloud/danish-foundation-models/default-models-configs/small-deberta-v2-32000-config.json \
    --dataset_name=dcc_v1.1.0 \
    --max_seq_length=512 \
    --learning_rate=6e-4 \
    --warmup_step=10000 \
    --adam_beta1=0.9 \
    --adam_beta2=0.98 \
    --adam_epsilon=1e-6 \
    --max_steps=100000 \
    --max_eval_samples=5000 \
    --logging_steps=100 \
    --eval_steps=2000 \
    --save_steps=2000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --do_train \
    --streaming \
    --seed=42 \
    --fp16 \
    --do_eval \
    --evaluation_strategy=steps \
    --nat_weight=0.60 \
    --danews_weight=0.20 \
    --hopetwitter_weight=0.10 \
    --dagw_dfm_weight=0.10 \
    --overwrite_output_dir \
    --per_device_train_batch_size=64 \
    --per_device_eval_batch_size=32 \
    --gradient_accumulation_steps=4 \
    --optim=adamw_torch \
    --overwrite_output_dir
```

- K. Enevoldsen (30- October, server: Grundtvig): Started running large-sized model.

Noted the lower learning rate is derrived from the deberta-v3 paper.

```bash
python src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/data-big-projects/danish-foundation-models/huggingface-repositories/dfm-debertav2-large-v1 \
    --tokenizer_name=/data-big-projects/danish-foundation-models/tokenizers/unigram_100000_docs_32000_vocab \
    --model_type=deberta-v2 \
    --use_pretrained_tokenizer \
    --config_name=/home/kenneth/github/danish-foundation-models/default-models-configs/large-deberta-v2-32000-config.json \
    --dataset_name=dcc_v1.1.0 \
    --max_seq_length=512 \
    --learning_rate=3e-4 \
    --warmup_step=10000 \
    --adam_beta1=0.9 \
    --adam_beta2=0.98 \
    --adam_epsilon=1e-6 \
    --max_steps=100000 \
    --max_eval_samples=5000 \
    --logging_steps=100 \
    --eval_steps=2000 \
    --save_steps=2000 \
    --push_to_hub \
    --weight_decay=0.01 \
    --do_train \
    --streaming \
    --seed=42 \
    --fp16 \
    --do_eval \
    --evaluation_strategy=steps \
    --nat_weight=0.60 \
    --danews_weight=0.20 \
    --hopetwitter_weight=0.10 \
    --dagw_dfm_weight=0.10 \
    --per_device_train_batch_size=64 \
    --per_device_eval_batch_size=64 \
    --optim=adamw_torch \
    --gradient_accumulation_steps=4 
    # --overwrite_output_dir
```

- K. Enevoldsen (31- October, server: Grundtvig): Restarted large-sized model as GPU
    utilization went to zero.
