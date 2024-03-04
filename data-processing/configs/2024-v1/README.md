# A common crawl dataset + (dagw, lexdk, scandi-reddit) with minimal amount of cleaning

The cleaning is run on ucloud `Terminal Ubuntu Jan2024`.


## Load Dependencies

```bash
module load Python/3.11.5-GCCcore-13.2.0
sudo apt-get update
# rust should be at least 1.72 (1.70 does not work)
sudo apt-get install rustc cargo
export GIT_SSH_COMMAND='ssh -i PATH/TO/PRIVATE/SSH_KEY -o IdentitiesOnly=yes'
```

## Install Data Processing Toolkit
```bash
git clone https://github.com/centre-for-humanities-computing/danish-foundation-models.git
cd danish-foundation-models/data-processing
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Run Taggers
```bash
cd configs/2024-v1
```

Run url blocklist tagger:
```bash
dolma -c dolma_run_url_taggers_mc4da_hplt.yaml tag
```

Run paragraph-level deduplication:

```bash
dolma -c dolma_dedupe_v1.yaml dedupe
```

## Mix Dataset

Since we did not run the URL tagger on the non-common-crawl datasets we hack a workaround and put in an empty placeholder attributes file.
In future datasets this should instead be configured in the mixer by using different streams.
```bash
mkdir /work/dfm-data/pre-training/dagw/v1blockurltaggers/
mkdir /work/dfm-data/pre-training/scandi-reddit/v1blockurltaggers/
mkdir /work/dfm-data/pre-training/lexdk/v1blockurltaggers/
touch /work/dfm-data/pre-training/dagw/v1blockurltaggers/data.jsonl
touch /work/dfm-data/pre-training/scandi-reddit/v1blockurltaggers/scandi-reddit.jsonl
touch /work/dfm-data/pre-training/lexdk/v1blockurltaggers/lexdk_articles.jsonl
gzip /work/dfm-data/pre-training/dagw/v1blockurltaggers/data.jsonl
gzip /work/dfm-data/pre-training/scandi-reddit/v1blockurltaggers/scandi-reddit.jsonl
gzip /work/dfm-data/pre-training/lexdk/v1blockurltaggers/lexdk_articles.jsonl
```

Finally mix the dataset:

```bash
dolma -c mix.yaml mix
```
