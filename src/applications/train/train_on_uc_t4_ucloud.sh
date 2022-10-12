# assumes:
# 1) ucloud rsync server is running w. ip 130.225.164.149 mounting the folder
# danish-foundation-models from the danish foundation models project
# 2) A uc t4 instance is running w. ip {IP}
# 3) The instance which this is run from has the private key for the uc t4 instance and 
# the ucloud rsync server (located in keys/ssh_key)
# Note: the ucloud rsync server could only be the instance you are running this script from

USER=ucloud
IP=130.225.38.153
RSYNC_DATA_FOLDER=/work/193701 #/work/danish-foundation-models

# ---
echo "Transfering ssh key to ucloud uc t4 instance"
scp -i keys/ssh_key train_on_uc_t4_ucloud.sh $USER@$IP:/work/keys

# ---
echo "Downloading data from ucloud server"
ssh -i keys/ssh_key $USER@$IP "rsync -avP -e "ssh -i ./ssh_key"  /data-big-projects/danish-foundation-models ucloud@$IP:$RSYNC_DATA_FOLDER"


# ---
echo "Setting up environment variables for ucloud t4 server"
ssh -i keys/ssh_key $USER@$IP "echo "" >> ~/.bashrc"
ssh -i keys/ssh_key $USER@$IP "echo "# Environment variables for Danish Foundation Models" >> ~/.bashrc"
ssh -i keys/ssh_key $USER@$IP "echo "export NAT_PATH='$RSYNC_DATA_FOLDER/netarkivet_cleaned/'" >> ~/.bashrc"
ssh -i keys/ssh_key $USER@$IP "echo "export DAGW_DFM_PATH='$RSYNC_DATA_FOLDER/dagw_cleaned/'" >> ~/.bashrc"
ssh -i keys/ssh_key $USER@$IP "echo "export DANEWS_PATH='$RSYNC_DATA_FOLDER/hope-infomedia_cleaned/'" >> ~/.bashrc"
ssh -i keys/ssh_key $USER@$IP "echo "export HOPETWITTER_PATH='$RSYNC_DATA_FOLDER/twitter_cleaned/'" >> ~/.bashrc"

ssh -i keys/ssh_key $USER@$IP "export NAT_PATH=$RSYNC_DATA_FOLDER/netarkivet_cleaned/"
ssh -i keys/ssh_key $USER@$IP "export DAGW_DFM_PATH=$RSYNC_DATA_FOLDER/dagw_cleaned/"
ssh -i keys/ssh_key $USER@$IP "export DANEWS_PATH=$RSYNC_DATA_FOLDER/hope-infomedia_cleaned/"
ssh -i keys/ssh_key $USER@$IP "export HOPETWITTER_PATH=$RSYNC_DATA_FOLDER/twitter_cleaned/"

# ---
echo "Clone danish foundation models repo"
ssh -i keys/ssh_key $USER@$IP "git clone https://github.com/centre-for-humanities-computing/danish-foundation-models"
echo "Changing branch to trainingv2"
ssh -i keys/ssh_key $USER@$IP "cd danish-foundation-models && git checkout trainingv2"
echo "Installing requirements"
ssh -i keys/ssh_key $USER@$IP "cd danish-foundation-models && pip install -r requirements.txt"

# ---
echo "Running training on ucloud t4 server"
TRAIN_COMMAND="python src/applications/train/run_mlm_pytorch_stream.py
    --output_dir=$RSYNC_DATA_FOLDER/danish-foundation-models/huggingface-repositories/dfm-roberta-small-v1
    --tokenizer_name=$RSYNC_DATA_FOLDER/danish-foundation-models/tokenizers/unigram_5000000_docs_32000_vocab
    --model_type=roberta
    --config_name=$RSYNC_DATA_FOLDER/danish-foundation-models/huggingface-repositories/dfm-roberta-small-v1
    --dataset_name=dcc_v1.1.0
    --max_seq_length=512
    --per_device_train_batch_size=128
    --per_device_eval_batch_size=128
    --learning_rate=2e-4
    --warmup_steps=10000
    --adam_beta1=0.9
    --adam_beta2=0.98
    --adam_epsilon=1e-6
    --max_steps=500000
    --max_eval_samples=5000
    --logging_steps=500
    --eval_steps=10000
    --push_to_hub
    --weight_decay=0.01
    --do_train
    --streaming
    --seed=42
    --fp16
    --do_eval
    --evaluation_strategy=steps
    --nat_weight=0.50
    --danews_weight=0.20
    --hopetwitter_weight=0.20
    --dagw_dfm_weight=0.10"

ssh -i keys/ssh_key $USER@$IP "cd /work/193701/danish-foundation-models/src/applications/train && $TRAIN_COMMAND"