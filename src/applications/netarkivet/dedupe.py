"""
Applies quality filters to Netarkivet filtering based on language tags.

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen

"""
from typing import Iterable, List

import glob
import os
import sys
from itertools import islice
from pathlib import Path
import multiprocessing
from functools import partial

from tqdm import tqdm
from wasabi import msg
import ndjson

from datasets import load_dataset

dfm_path = os.path.join("danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import Deduper


def filter_example(example, already_checked):
    """check whether sample i should be included"""
    return example["language"] in {"da"} and example["passed_quality_filter"] is True and example["id"] not in already_checked

def get_id_from_path(x):
    return int(os.path.split(x)[-1].split(".")[0])

def create_paths(years = [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]):
    for year in years:
        read_path = os.path.join("/work", "netarkivet-cleaned", f"{year}")
        path = os.path.join(read_path, "**", "*.jsonl")
        jsonl_files = glob.glob(path, recursive=True)
        jsonl_files = sorted(jsonl_files, key=lambda x: get_id_from_path(x))
        for jf in jsonl_files:
            msg.info(f"Currently processing {jf}")
            i = get_id_from_path(jf)
            yield year, i, jf
        msg.good(f"Finished year {year}")


def create_text_gen(
    already_checked: set,
    paths: Iterable[str]
):
    filter_example_ = partial(filter_example, already_checked = already_checked)
    
    for year, i, j_files in paths:

        with open(j_files) as f:
            reader = ndjson.reader(f)

            for id, website in enumerate(reader):
                website["id"] = f"{year}_{i}_{id}"
                if filter_example_(website):
                    yield website["id"], website["text"]


def main(
    dedupe_path: str,
) -> None:
    if os.path.exists(dedupe_path):
        msg.info(f"Loading Deduper from {dedupe_path}")
        deduper = Deduper.load_from_disk(dedupe_path)
        already_checked = {d["id"] for d in deduper.mask}
    else:
        deduper = Deduper(batch_size=2**20) # potentially change to 2**23
        already_checked = set()

    for year in [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]:
        paths = create_paths(years = [year])
        text_gen = create_text_gen(already_checked=already_checked, paths=paths)

        dedupe_path_ =  os.path.join(dedupe_path, str(year))

        deduper.deduplicate(text_gen, return_generator=False, overwrite=True, store_corpus_to_disk = False, 
            store_mask_to_disk = True, store_lsh_cache_to_disk = True, store_config_to_disk = True, output_dir=dedupe_path_)



if __name__ == "__main__":
    dedupe_path = os.path.join("/work", "netarkivet-cleaned", "deduplicated")
    main(dedupe_path)
