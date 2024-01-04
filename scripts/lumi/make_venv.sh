#!/bin/bash
# Important: should be run in the `rocm/pytorch`` container
set -euxo pipefail
export LC_ALL=C

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
GIT_ROOT=$(git rev-parse --show-toplevel)

cd ${GIT_ROOT}
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install packaging cmake # build requirements

#cd ${GIT_ROOT}/llm-foundry
#pip install -e .

pip install -r ${SCRIPT_DIR}/requirements.txt

# Install flash attention
TMP_DIR=$(mktemp -d)
git clone --recurse-submodules https://github.com/ROCmSoftwarePlatform/flash-attention ${TMP_DIR}
cd ${TMP_DIR}

## apply a patch to set compilation target (no longer needed, FA2 added an easier way)
# cat << EOF > arch.patch
# diff --git a/setup.py b/setup.py
# index edbba24..2813e00 100644
# --- a/setup.py
# +++ b/setup.py
# @@ -207,7 +207,7 @@ if not IS_ROCM_PYTORCH:
#  else:
#  # build for ROCm
#    cc_flag = []
# -  cc_flag.append("--offload-arch=native")
# +  cc_flag.append("--offload-arch=gfx90a")
                         
#    if int(os.environ.get('FLASH_ATTENTION_INTERNAL_USE_RTN', 0)):
#      print("RTN IS USED")
# EOF

# git apply arch.patch

export GPU_ARCHS="gfx90a"

# export PYTHON_SITE_PACKAGES=$(python -c 'import site; print(site.getsitepackages()[0])') # this is for older versions of pytorch
# patch "${PYTHON_SITE_PACKAGES}/torch/utils/hipify/hipify_python.py" hipify_patch.patch
python3 setup.py install