#!/bin/bash

##SBATCH --exclude=nid006865,nid005613,nid005988
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
##SBATCH --cpus-per-task=56
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
module load LUMI/22.08 partition/G singularity-bindings/system-cpeGNU-22.08-noglibc
export SINGULARITY_BIND=/users/larsenra/aws-ofi-rccl/install:/opt/aws-ofi-rccl,/usr/lib64/libjitterentropy.so.3,${SINGULARITY_BIND}
export SINGULARITYENV_LD_LIBRARY_PATH=/opt/ompi/lib:${EBROOTAWSMINOFIMINRCCL}/lib:/opt/cray/xpmem/2.5.2-2.4_3.47__gd0f7936.shasta/lib64:/opt/aws-ofi-rccl/lib:${SINGULARITYENV_LD_LIBRARY_PATH}
export SINGULARITY_BIND=$(echo $SINGULARITY_BIND | sed 's|,/usr/lib64/libssh.so.4||g') # do not bind host libssh which is built against a wrong libssl for some reason
export LC_ALL=C
export HF_DATASETS_CACHE="/scratch/project_465000670/.cache/huggingface" 
export TRANSFORMERS_CACHE="/scratch/project_465000670/.cache/huggingface"

# values for distributed setup 
GPUS_PER_NODE=8
NNODES=$SLURM_NNODES
NODE_RANK=$SLURM_PROCID
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT=9999
export WORLD_SIZE=$(($GPUS_PER_NODE*$NNODES))

# compilers in the container
export CC=gcc-11
export CXX=g++-11

CONTAINER="/project/project_465000670/pytorch_rocm5.7_ubuntu22.04_py3.10_pytorch_2.0.1.sif"

SING_BIND="/scratch/project_465000670"

# hold separate logs for easier debugging
rm -rf separate-logs
mkdir -p separate-logs

set -exuo pipefail

# symlink logs/latest.out and logs/latest.err
ln -f -s $SLURM_JOB_ID.out logs/latest.out
ln -f -s $SLURM_JOB_ID.err logs/latest.err

CHECKPOINT_PATH=checkpoints

mkdir -p ds_configs
DS_CONFIG_PATH="ds_configs/$SLURM_JOB_ID.json"
cat <<EOF > $DS_CONFIG_PATH
{
    "train_micro_batch_size_per_gpu": "auto",
    "train_batch_size": "auto",
    "gradient_accumulation_steps": "auto",
    "gradient_clipping": 1.0,
    "zero_optimization": {
        "stage": 3,
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

CMD=" \
    continue_mistral.py \
    --deepspeed $DS_CONFIG_PATH
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
    ./accelerate_in_container.sh \
    $CMD

echo "END $SLURM_JOBID: $(date)"