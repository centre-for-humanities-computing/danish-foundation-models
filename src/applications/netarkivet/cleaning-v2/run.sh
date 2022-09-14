# cleaning
# clean 2006
python3 danish-foundation-models/src/dfm/cleaning/clean.py \
    path=/work/netarchive/2006_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2 \
    text_col=content \
    lang_col=language \
    num_proc=31 

python3 danish-foundation-models/src/dfm/cleaning/clean.py \
    path=/work/netarchive/2016_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2016 \
    text_col=content \
    lang_col=language \
    num_proc=31 

python3 danish-foundation-models/src/dfm/cleaning/clean.py \
    path=/work/netarchive/2015_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2015 \
    text_col=content \
    lang_col=language \
    num_proc=31