# sets the path for NAT_PATH, DANEWS_PATH, DAGW_DFM_PATH and HOPETWITTER_PATH
# for the train application


if [ -v NAT_PATH ] && [ -v DAGW_DFM_PATH ] && [ -v DANEWS_PATH ] && [ -v HOPETWITTER_PATH ]; then
    echo "Environment variables for DFM already set"
else
    # if server has /data-big-projects/danish-foundation-models/ directory then it must be the Grundtvig server
    if [ -d /data-big-projects/danish-foundation-models/ ]; then
        echo "Setting environment variables for Grundtvig server"

        DFM_PATH=/data-big-projects/danish-foundation-models
        # append to .bashrc
        echo "" >> ~/.bashrc
        echo "# Environment variables for Danish Foundation Models" >> ~/.bashrc
        echo "export NAT_PATH='$DFM_PATH/netarkivet_cleaned/'" >> ~/.bashrc
        echo "export DAGW_DFM_PATH='$DFM_PATH/dagw_cleaned/'" >> ~/.bashrc
        echo "export DANEWS_PATH='$DFM_PATH/hope-infomedia_cleaned/'" >> ~/.bashrc
        echo "export HOPETWITTER_PATH='$DFM_PATH/twitter_cleaned/'" >> ~/.bashrc

        export NAT_PATH=$DFM_PATH/netarkivet_cleaned/
        export DAGW_DFM_PATH=$DFM_PATH/dagw_cleaned/
        export DANEWS_PATH=$DFM_PATH/hope-infomedia_cleaned/
        export HOPETWITTER_PATH=$DFM_PATH/twitter_cleaned/


    # if server has /work/ it must be a Ucloud instance
    elif [ -d /work/ ]; then
        echo "Setting environment variables for Ucloud instance"

        DFM_PATH=/work/dfm-data
        echo "" >> ~/.bashrc
        echo "# Environment variables for Danish Foundation Models" >> ~/.bashrc
        echo "export NAT_PATH='$DFM_PATH/netarkivet-cleaned/'" >> ~/.bashrc
        echo "export DAGW_DFM_PATH='$DFM_PATH/dagw-cleaned/'" >> ~/.bashrc
        echo "export DANEWS_PATH='$DFM_PATH/hope-infomedia_cleaned/'" >> ~/.bashrc
        echo "export HOPETWITTER_PATH='$DFM_PATH/twitter_cleaned/'" >> ~/.bashrc

        export NAT_PATH=$DFM_PATH/netarkivet-cleaned/
        export DAGW_DFM_PATH=$DFM_PATH/dagw-cleaned/
        export DANEWS_PATH=$DFM_PATH/hope-infomedia_cleaned/
        export HOPETWITTER_PATH=$DFM_PATH/twitter_cleaned/

    
    else
        echo "Could not set environment variables for DFM"
    fi
fi


echo "Checking paths:"
echo "NAT_PATH: $NAT_PATH"
echo "DANEWS_PATH: $DANEWS_PATH"
echo "DAGW_DFM_PATH: $DAGW_DFM_PATH"
echo "HOPETWITTER_PATH: $HOPETWITTER_PATH"
