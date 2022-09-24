################################################
# Cleaning
################################################

# clean 2006
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2006_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2006 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2007
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2007_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2007 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2008
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2008_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2008 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2009
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2009_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2009 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2010
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2010_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2010 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2011
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2011_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2011 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2012
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2012_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2012 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2013
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2013_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2013 \
    text_col=content \
    lang_col=language \
    num_proc=32


# clean 2014
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2014_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2014 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2015
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2015_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2015 \
    text_col=content \
    lang_col=language \
    num_proc=32

# clean 2016
python3 danish-foundation-models/src/dfm/cleaning/clean_cli.py \
    path=/work/netarchive/2016_textcorpus.parquet/*.parquet \
    save_dir=/work/netarkivet-cleaned/v2/2016 \
    text_col=content \
    lang_col=language \
    num_proc=32 


################################################
# Deduplication
################################################

python3 danish-foundation-models/src/dfm/cleaning/dedupe_cli.py \
    path="/work/netarkivet-cleaned/v2/2006/*.jsonl" \
    save_dir=/work/netarkivet-cleaned/v2/2006 \
    text_col=content \
    num_proc=31 \
    verbosity_level=1

python3 danish-foundation-models/src/dfm/cleaning/dedupe_cli.py \
    path="/work/netarkivet-cleaned/v2/2007/*.jsonl" \
    save_dir=/work/netarkivet-cleaned/v2/2007/deduplicated/ \
    text_col=content \
    num_proc=31 \
    verbosity_level=1


python3 danish-foundation-models/src/dfm/cleaning/dedupe_cli.py \
    path="/work/netarkivet-cleaned/v2/2008/*.jsonl" \
    save_dir=/work/netarkivet-cleaned/v2/2008/deduplicated/ \
    text_col=content \
    num_proc=31 \
    verbosity_level=1


python3 danish-foundation-models/src/dfm/cleaning/dedupe_cli.py \
    path="/work/netarkivet-cleaned/v2/2009/*.jsonl" \
    save_dir=/work/netarkivet-cleaned/v2/2009/deduplicated/ \
    text_col=content \
    num_proc=31 \
    verbosity_level=1
