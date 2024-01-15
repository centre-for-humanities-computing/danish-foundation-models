# Model training on LUMI

## Dataset preparation
From a jsonl file (such as da-gigaword), something like `python scripts/data/convert_dataset_json.py --path /path/to/da-gigaword.jsonl.tar.gz  --out_root ./da-gigaword-mds --concat_tokens 4096 --tokenizer mistralai/Mistral-7B-v0.1 --test_size 0.02` will generate the necessary Mosaic streaming dataset. Takes ~2 hours for da-gigaword, which is a bit slow. When done, copy this folder to LUMI scratch and configure data path in the training YAML, e.g. `scripts/lumi/yamls/continue-mistral-7b.yaml`.

## LUMI setup and training
1. SSH into LUMI
3. Enter project: `cd /scratch/project_465000670/danish-foundation-models`
2. Enter container: `singularity run --cleanenv --bind /scratch/project_465000670/ /project/project_465000670/pytorch_rocm5.7_ubuntu22.04_py3.10_pytorch_2.0.1.sif`
5. Set up virtual environment: `./scripts/lumi/make_venv.sh`
6. Exit container
7. Run training: `./scripts/lumi/continue_mistral_mosaic.sh`
