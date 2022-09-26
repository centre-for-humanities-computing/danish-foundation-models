
################################################
# Deduplication
################################################

# python3 danish-foundation-models/src/dfm/cleaning/dedupe_cli.py \
#     path="/work/netarkivet-cleaned/v2/2006/*.jsonl" \
#     save_dir=/work/netarkivet-cleaned/v2/2006 \
#     text_col=content \
#     num_proc=32

# python3 danish-foundation-models/src/dfm/cleaning/dedupe_cli.py \
#     path="/work/netarkivet-cleaned/v2/2007/*.jsonl" \
#     save_dir=/work/netarkivet-cleaned/v2/2007/deduplicated/ \
#     text_col=content \
#     num_proc=32

for YEAR in {2008..2016}
do
    echo "$YEAR"
    python3 danish-foundation-models/src/dfm/cleaning/dedupe_cli.py \
        path="/work/netarkivet-cleaned/v2/$YEAR/*.jsonl" \
        save_dir=/work/netarkivet-cleaned/v2/$YEAR/deduplicated/ \
        text_col=content \
        num_proc=32

done

