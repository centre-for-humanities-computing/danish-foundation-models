#!/bin/bash
# Launch script used by slurm scripts, don't invoke directly.
set -euxo pipefail

# script starts with pwd in the users home directory, so we need to cd to our repo
cd /scratch/project_465000670/danish-foundation-models

source .venv/bin/activate

# Samuel's fix for apparent error in SLURM initialization 
if [ $SLURM_LOCALID -eq 0 ]; then
    rm -rf /dev/shm/*
    rocm-smi || true
else
    sleep 2
fi

# Hoping to resolve "Cassini Event Queue overflow detected." errors
export FI_CXI_DEFAULT_CQ_SIZE=262144    # default 131072

echo "Rank $SLURM_PROCID CPU affinity: $(taskset -p $$)"

export NCCL_SOCKET_IFNAME=hsn0,hsn1,hsn2,hsn3
export OMP_NUM_THREADS=1

export TORCH_EXTENSIONS_DIR=torch_extensions
mkdir -p $TORCH_EXTENSIONS_DIR

export NCCL_DEBUG=INFO
# export PYTORCH_HIP_ALLOC_CONF=garbage_collection_threshold:0.8,max_split_size_mb:128 # Trying to fix a memory access error

# values for distributed setup (for some reason these have to be set again after continue_mistral_mosaic.sh)
GPUS_PER_NODE=$SLURM_GPUS_ON_NODE # assuming same number of GPUs per node
NNODES=$SLURM_NNODES
export NODE_RANK=$SLURM_NODEID
export WORLD_SIZE=$(($GPUS_PER_NODE*$NNODES))

echo "Launching on $SLURMD_NODENAME ($SLURM_PROCID/$SLURM_JOB_NUM_NODES)," \
     "NODE_RANK=$NODE_RANK, WORLD_SIZE=$WORLD_SIZE" \
     "master $MASTER_ADDR port $MASTER_PORT," \
     "GPUs $SLURM_GPUS_ON_NODE," \
     "ROCm: $(python -c 'import torch; print(torch.cuda.is_available())')"

composer \
    "$@" \
    > >(tee separate-logs/${SLURMD_NODENAME}-${SLURM_PROCID}.out) \
    2> >(tee separate-logs/${SLURMD_NODENAME}-${SLURM_PROCID}.err)

