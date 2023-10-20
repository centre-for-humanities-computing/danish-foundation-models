#!/bin/bash

# Launch script used by slurm scripts, don't invoke directly.

source .hfvenv-5.7/bin/activate

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

GPUS_PER_NODE=8
NNODES=$SLURM_NNODES
NODE_RANK=$SLURM_PROCID
export RANK=$SLURM_PROCID
export LOCAL_RANK=$SLURM_LOCALID

mkdir -p configs
ACCELERATE_CONFIG_PATH="configs/accelerate-$SLURMD_NODENAME-$SLURM_PROCID.yaml"
DS_CONFIG_PATH="configs/ds-$SLURMD_NODENAME-$SLURM_PROCID.json"

cat <<EOF > $ACCELERATE_CONFIG_PATH
compute_environment: LOCAL_MACHINE
deepspeed_config: 
    deepspeed_config_file: $DS_CONFIG_PATH
    zero3_init_flag: false
distributed_type: DEEPSPEED
downcast_bf16: 'no'
machine_rank: $SLURM_PROCID
main_process_ip: $MASTER_ADDR
main_process_port: $MASTER_PORT
main_training_function: main
num_machines: $SLURM_NNODES
num_processes: $WORLD_SIZE
rdzv_backend: static
same_network: true
tpu_env: []
tpu_use_cluster: false
tpu_use_sudo: false
use_cpu: false
EOF



export NCCL_DEBUG=INFO
export PYTORCH_HIP_ALLOC_CONF=garbage_collection_threshold:0.8,max_split_size_mb:128 # Trying to fix a memory access error

echo "Launching on $SLURMD_NODENAME ($SLURM_PROCID/$SLURM_JOB_NUM_NODES)," \
     "master $MASTER_ADDR port $MASTER_PORT," \
     "GPUs $SLURM_GPUS_ON_NODE," \
     "CUDA: $(python -c 'import torch; print(torch.cuda.is_available())')"

python -m torch.distributed.run \
    --nproc_per_node 8 --nnodes $SLURM_NNODES --node_rank $SLURM_PROCID \
    --master_addr $MASTER_ADDR --master_port $MASTER_PORT \
    "$@" \
    > >(tee separate-logs/${SLURMD_NODENAME}-${SLURM_PROCID}.out) \
    2> >(tee separate-logs/${SLURMD_NODENAME}-${SLURM_PROCID}.err)

#accelerate launch --config_file $ACCELERATE_CONFIG_PATH "$@" \
#    > >(tee separate-logs/${SLURMD_NODENAME}-${SLURM_PROCID}.out) \
#    2> >(tee separate-logs/${SLURMD_NODENAME}-${SLURM_PROCID}.err)