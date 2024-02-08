#!/bin/bash
# Important: should be run in the `rocm/pytorch`` container
set -euxo pipefail
export LC_ALL=C

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
GIT_ROOT=$(git rev-parse --show-toplevel)

cd ${SCRIPT_DIR}
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install packaging cmake # build requirements

# Install pytorch
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm5.7

# Install flash attention
TMP_DIR=$(mktemp -d)
git clone --recurse-submodules https://github.com/ROCmSoftwarePlatform/flash-attention ${TMP_DIR}
cd ${TMP_DIR}
export GPU_ARCHS="gfx90a"
python3 setup.py install

# Install vllm
TMP_DIR=$(mktemp -d)
git clone https://github.com/rlrs/vllm.git ${TMP_DIR} # vllm fork until they fix 
cd ${TMP_DIR}
pip install xformers==0.0.23 --no-deps # this step is from the vllm docs
bash patch_xformers.rocm.sh # so is this
pip install -U -r requirements-rocm.txt
python setup.py install # builds for GPU_ARCHS

# Install scandeval
pip install scandeval