#!/bin/bash
# Important: should be run in the `rocm/pytorch`` container
set -euxo pipefail
export LC_ALL=C

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
GIT_ROOT=$(git rev-parse --show-toplevel)

cd ${SCRIPT_DIR}
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install packaging cmake # build requirements

cd ${SCRIPT_DIR}/llm-foundry
pip install -e .
pip install mosaicml-turbo==0.0.8 # consider what to do with this dependency from .[gpu]

pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7 --upgrade

# Install flash attention
TMP_DIR=$(mktemp -d)
git clone --recurse-submodules https://github.com/ROCmSoftwarePlatform/flash-attention ${TMP_DIR}
cd ${TMP_DIR}

export GPU_ARCHS="gfx90a"
export MAX_JOBS=12 # be nice on the login nodes

# export PYTHON_SITE_PACKAGES=$(python -c 'import site; print(site.getsitepackages()[0])') # this is for older versions of pytorch
# patch "${PYTHON_SITE_PACKAGES}/torch/utils/hipify/hipify_python.py" hipify_patch.patch
python3 setup.py install