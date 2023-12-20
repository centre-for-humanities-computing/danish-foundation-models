# Model training on LUMI

1. SSH into LUMI
3. Enter project: `cd /scratch/project_465000670/danish-foundation-models`
2. Enter container: `singularity run --cleanenv --bind /scratch/project_465000670/ /project/project_465000670/pytorch_rocm5.7_ubuntu22.04_py3.10_pytorch_2.0.1.sif`
5. Set up virtual environment: `./src/dfm/projects/production/model_training/scripts/make_venv.sh`
6. Exit container
7. Run training: `./src/dfm/projects/production/model_training/scripts/continue_mistral_mosaic.sh`
