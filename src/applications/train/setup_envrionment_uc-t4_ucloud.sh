# assumes:
# 1) ucloud rsync server is running w. ip {RSYNC_IP} with following folder mounted:
# danish-foundation-models/dfm-data (project: Danish Foundation Models) 
# 2) Run from a a uc t4 instance is running where you have initially run:
# git clone https://github.com/centre-for-humanities-computing/danish-foundation-models
# git checkout trainingv2
# 3) a private key is located at {SSH_KEY_RSYNC_PATH}.
# Note: the ucloud rsync server could only be the instance you are running this script from

## === SETUP === ##

## Transfer Data setup
RSYNC_DATA_FOLDER=dfm-data
RSYNC_IP=130.225.164.149
SSH_KEY_RSYNC_PATH=/home/ucloud/.ssh/ssh_key_rsync
RSYNC_USER=ucloud
DATA_DIR=~/data

## Model repo setup
HF_REPO_FOLDER=/home/ucloud/data/dfm-data/huggingface-repositories
MODEL_NAME=dfm-debertav2-small-v1

# training setup
DFM_PATH=~/danish-foundation-models

# set git configs
git config --global user.email "kennethcenevoldsen@gmail.com"
git config --global user.name "Kenneth Enevoldsen (UCloud uc-t4)"
git config --global credential.helper store


## === DOWNLOAD DATA === ##

# check that data dir exist otherwise create it
if [ ! -d "$DATA_DIR" ]; then
    mkdir -p $DATA_DIR
fi

# move data using rsync if not already there
rsync -avP -e "ssh -i $SSH_KEY_RSYNC_PATH" $RSYNC_USER@$RSYNC_IP:/work/$RSYNC_DATA_FOLDER $DATA_DIR


# setup paths for data
echo "" >> ~/.bashrc
echo "# Environment variables for Danish Foundation Models" >> ~/.bashrc
echo "export NAT_PATH='$DATA_DIR/$RSYNC_DATA_FOLDER/netarkivet-cleaned/'" >> ~/.bashrc
echo "export DAGW_DFM_PATH='$DATA_DIR/$RSYNC_DATA_FOLDER/dagw-cleaned/'" >> ~/.bashrc
echo "export DANEWS_PATH='$DATA_DIR/$RSYNC_DATA_FOLDER/hope-infomedia_cleaned/'" >> ~/.bashrc
echo "export HOPETWITTER_PATH='$DATA_DIR/$RSYNC_DATA_FOLDER/twitter_cleaned/'" >> ~/.bashrc

## === SETUP MODEL REPOSITORY === ##

# setup pip
sudo apt-get update -y
sudo apt-get install python3-pip -y

# add python path to bashrc
echo 'export PATH="/home/ucloud/.local/bin:$PATH"' >> ~/.bashrc

# install huggingface_hub
pip install pip --upgrade
pip install huggingface_hub

# login to huggingface hub
huggingface-cli login

# initialize HF model
cd $HF_REPO_FOLDER
git clone https://huggingface.co/chcaa/$MODEL_NAME
cd $MODEL_NAME

# setup git lfs
sudo apt-get install git-lfs
git lfs install
huggingface-cli lfs-enable-largefiles .

## === TRAIN MODEL === ##

# install requirements
cd $DFM_PATH
pip install -e . 

# train model
python3 src/applications/train/run_mlm_pytorch_stream.py \
    --output_dir=/data/dfm-data/huggingface-repositories/dfm-debertav2-small-v1 \
    --tokenizer_name=/data/dfm-data/tokenizers/unigram_100000_docs_32000_vocab \
    --model_type=deberta-v2 \
    --use_pretrained_tokenizer \
    --config_name=~/danish-foundation-models/default-models-configs/small-deberta-v2-32000-config.json \
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
    --eval_steps=2 \
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
    --per_device_train_batch_size=256 \
    --per_device_eval_batch_size=128 \
    --gradient_accumulation_steps=2 \
    --optim=adamw_torch \
    --overwrite_output_dir
    # eval_steps=2000

# update cuda drivers
sudo apt update
sudo apt full-upgrade -y
sudo apt install nvidia-headless-460 nvidia-utils-460 -y
sudo reboot