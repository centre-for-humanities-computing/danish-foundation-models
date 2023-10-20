#!/bin/bash

#SBATCH --exclude=nid006865,nid005613,nid005988
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=8
##SBATCH --cpus-per-task=8
#SBATCH --mem=0
#SBATCH --partition=standard-g
#SBATCH --time=0-00:30:00
#SBATCH --gpus-per-node=mi250:8
#SBATCH --exclusive=user
#SBATCH --hint=nomultithread
#SBATCH --account=project_465000670
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

# if run without sbatch, invoke here
if [ -z $SLURM_JOB_ID ]; then
    mkdir -p logs
    sbatch "$0"
    exit
fi

# LUMI setup
module load LUMI/22.08 partition/G singularity-bindings
export SINGULARITY_BIND=/users/larsenra/aws-ofi-rccl/install:/opt/aws-ofi-rccl,/usr/lib64/libjitterentropy.so.3,${SINGULARITY_BIND}
export SINGULARITYENV_LD_LIBRARY_PATH=/opt/ompi/lib:${EBROOTAWSMINOFIMINRCCL}/lib:/opt/cray/xpmem/2.5.2-2.4_3.47__gd0f7936.shasta/lib64:/opt/aws-ofi-rccl/lib:${SINGULARITYENV_LD_LIBRARY_PATH}
export SINGULARITY_BIND=$(echo $SINGULARITY_BIND | sed 's|,/usr/lib64/libssh.so.4||g') # do not bind host libssh which is built against a wrong libssl for some reason

# distributed setup
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT=9999
export WORLD_SIZE=$SLURM_NTASKS

# compilers in the container
export CC=gcc-9
export CXX=g++-9

# singularity setup
#CONTAINER="pytorch-lumi_sles-rocm-5.5.1-python-3.10-pytorch-v2.0.1-apex-torchvision-torchdata-torchtext-torchaudio.sif"
CONTAINER="/project/project_465000670/rocm-5.4.2.sif"

SING_BIND="/scratch/project_465000670"

#export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"

# hold separate logs for easier debugging
rm -rf separate-logs
mkdir -p separate-logs

set -exuo pipefail

# symlink logs/latest.out and logs/latest.err
ln -f -s $SLURM_JOB_ID.out logs/latest.out
ln -f -s $SLURM_JOB_ID.err logs/latest.err

CHECKPOINT_PATH=checkpoints
TENSORBOARD_PATH=tensorboard
#rm -rf "$CHECKPOINT_PATH" "$TENSORBOARD_PATH" # Start from scratch

# Data
TRAIN_DATA_PATH="data/wikipedia_20220301.en.train_text_document"
VALID_DATA_PATH="data/wikipedia_20220301.en.valid_text_document"
TOKENIZER_PATH="tokenizer"

PP_SIZE=1
TP_SIZE=2
ZERO_STAGE=2

MICRO_BATCH_SIZE=4
GLOBAL_BATCH_SIZE=1024 # e.g. llama: 4M tokens

TRAIN_SAMPLES=146_500_000
TRAIN_SAMPLES=${TRAIN_SAMPLES//_}    # drop "_" for bash math
LR=3e-4
MIN_LR=3e-5
LR_DECAY_SAMPLES=$TRAIN_SAMPLES
LR_WARMUP_SAMPLES=$((TRAIN_SAMPLES/100))
WEIGHT_DECAY=0.1
GRAD_CLIP=1

HIDDEN_SIZE=4096 # e.g. llama-7b: 4096, llama-13b: 5120
FFN_HIDDEN_SIZE=11008 # e.g. llama-7b: 11008, llama-13b: 13824
NUM_LAYERS=32 # e.g. llama-7b: 32, llama-13b: 40
NUM_HEADS=32 # e.g. llama-7b: 32, llama-13b: 40
SEQ_LENGTH=2048
NUM_KV_HEADS=32 # llama2 70B uses GQA (4)

SAVE_INTERVAL=1000
OPTIMIZER_ARGS=" \
    --optimizer adam \
    --adam-beta1 0.9 \
    --adam-beta2 0.95 \
    --lr $LR \
    --min-lr $MIN_LR \
    --lr-decay-style cosine \
    --lr-decay-samples $LR_DECAY_SAMPLES \
    --lr-warmup-samples $LR_WARMUP_SAMPLES \
    --clip-grad $GRAD_CLIP \
    --weight-decay $WEIGHT_DECAY \
    "


## Activation checkpointing saves GPU memory, but reduces training speed
# activation_checkpoint="true"
activation_checkpoint="false"

# Below configuration required for llama model as per llama paper
# --no-query-key-layer-scaling \
# --attention-dropout 0 \
# --hidden-dropout 0 \
# --use-rotary-position-embeddings \
# --untie-embeddings-and-output-weights \
# --swiglu \
# --normalization rmsnorm \
# --disable-bias-linear \

GPT_ARGS=" \
    --num-layers $NUM_LAYERS \
    --hidden-size $HIDDEN_SIZE \
    --num-attention-heads $NUM_HEADS \
    --ffn-hidden-size $FFN_HIDDEN_SIZE \
    --seq-length $SEQ_LENGTH \
    --max-position-embeddings $SEQ_LENGTH \
    --micro-batch-size $MICRO_BATCH_SIZE \
    --global-batch-size $GLOBAL_BATCH_SIZE \
    --train-samples $TRAIN_SAMPLES \
    --tokenizer-type GPT2BPETokenizer \
    --vocab-file vocab.json \
    --merge-file merges.txt \
    --init-method-std 0.0048 \
    --bf16 \
    --seed 42 \
    --use-rotary-position-embeddings \
    --untie-embeddings-and-output-weights \
    --swiglu \
    --normalization rmsnorm \
    --disable-bias-linear \
    --num-key-value-heads $NUM_KV_HEADS \
    --attention-dropout 0 \
    --hidden-dropout 0 \
    --use-flash-attn-v1 \
    --make-vocab-size-divisible-by 128 \
    --no-gradient-accumulation-fusion \
    $OPTIMIZER_ARGS \
    "

OUTPUT_ARGS=" \
    --log-interval 1 \
    --save-interval $SAVE_INTERVAL \
    --eval-interval 1000 \
    --eval-iters 10 \
    --tensorboard-dir $TENSORBOARD_PATH \
    --tensorboard-queue-size 5 \
    --log-timers-to-tensorboard \
    --log-batch-size-to-tensorboard \
    --log-validation-ppl-to-tensorboard \
    "


mkdir -p ds_configs
DS_CONFIG_PATH="ds_configs/$SLURM_JOB_ID.json"

cat <<EOF > $DS_CONFIG_PATH
{
    "train_micro_batch_size_per_gpu": $MICRO_BATCH_SIZE,
    "train_batch_size": $GLOBAL_BATCH_SIZE,
    "gradient_clipping": 1.0,
    "zero_optimization": {
        "stage": $ZERO_STAGE,
        "reduce_bucket_size": 10000000,
        "reduce_scatter": true,
        "zero_hpz_partition_size": 8,
        "contiguous_gradients": true,
        "overlap_comm": true
    },
    "bf16": {
        "enabled": true
    },
    "data_types": { "grad_accum_dtype": "fp32" },
    "steps_per_print": 100,
    "wall_clock_breakdown": false
}
EOF

DEEPSPEED_ARGS=" \
    --deepspeed \
    --deepspeed_config $DS_CONFIG_PATH \
    --zero-stage $ZERO_STAGE \
    "

CMD=" \
    Megatron-DeepSpeed/pretrain_gpt.py \
    --tensor-model-parallel-size $TP_SIZE \
    --no-pipeline-parallel \
    --pipeline-model-parallel-size $PP_SIZE \
    $GPT_ARGS \
    $OUTPUT_ARGS \
    --save $CHECKPOINT_PATH \
    --load $CHECKPOINT_PATH \
    --train-data-path $TRAIN_DATA_PATH \
    --valid-data-path $VALID_DATA_PATH \
    --data-impl mmap \
    --dataloader-type single
    --num-workers 2 \
     $DEEPSPEED_ARGS \
    "

# Bind masks from Samuel
c=fe

# Bind mask for one thread per core
BIND_MASK_1="0x${c}000000000000,0x${c}00000000000000,0x${c}0000,0x${c}000000,0x${c},0x${c}00,0x${c}00000000,0x${c}0000000000"

# Bind mask for two threads per core
BIND_MASK_2="0x${c}00000000000000${c}000000000000,0x${c}00000000000000${c}00000000000000,0x${c}00000000000000${c}0000,0x${c}00000000000000${c}000000,0x${c}00000000000000${c},0x${c}00000000000000${c}00,0x${c}00000000000000${c}00000000,0x${c}00000000000000${c}0000000000"

BIND_MASK="$BIND_MASK_1"
echo "Using --cpu-bind=mask_cpu:$BIND_MASK"

echo $CMD

echo "START $SLURM_JOBID: $(date)"

srun \
    --label \
    --cpu-bind=mask_cpu:$BIND_MASK \
    singularity exec -B "$SING_BIND" "$CONTAINER" \
    ./launch.sh \
    $CMD

echo "END $SLURM_JOBID: $(date)"
