# assumes:
# 1) ucloud rsync server is running w. ip {RSYNC_IP} with following folder mounted:
# danish-foundation-models/dfm-data (project: Danish Foundation Models) 
# 2) Run from a a uc t4 instance is running where you have initially run:
# git clone https://github.com/centre-for-humanities-computing/danish-foundation-models
# git checkout trainingv2
# 3) a private key is located at {SSH_KEY_RSYNC_PATH}.
# Note: the ucloud rsync server could only be the instance you are running this script from

RSYNC_DATA_FOLDER=dfm-data
RSYNC_IP=130.225.164.149
SSH_KEY_RSYNC_PATH=/home/ucloud/.ssh/ssh_key_rsync
RSYNC_USER=ucloud
DATA_DIR=~/data

# set git configs
git config --global user.email "kennethcenevoldsen@gmail.com"
git config --global user.name "Kenneth Enevoldsen (UCloud uc-t4)"

# check that data dir exist otherwise create it
if [ ! -d "$DATA_DIR" ]; then
    mkdir -p $DATA_DIR
fi

# move data using rsync if not already there
rsync -avP -e "ssh -i $SSH_KEY_RSYNC_PATH" $RSYNC_USER@$RSYNC_IP:/work/$RSYNC_DATA_FOLDER $DATA_DIR
