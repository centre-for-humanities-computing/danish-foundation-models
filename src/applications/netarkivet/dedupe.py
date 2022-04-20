"""
Applies quality filters to Netarkivet filtering based on language tags.

Dependent on:
    src/applications/netarkivet/quality_filter.py

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

import psutil  
from psutil._common import bytes2human

from dfm.cleaning import Deduper


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
            i = get_id_from_path(jf)
            yield year, i, jf
        msg.good(f"Finished year {year}")


def create_text_gen(
    already_checked: set,
    paths: Iterable[str]
):
    filter_example_ = partial(filter_example, already_checked = already_checked)
    
    for year, i, j_files in paths:
        msg.info(f"Currently processing {j_files}")
        with open(j_files) as f:
            reader = ndjson.reader(f)

            for id, website in enumerate(reader):
                website["id"] = f"{year}_{i}_{id}"
                if filter_example_(website):
                    yield website["id"], website["text"]


def main(
    dedupe_path: str,
) -> None:
    for year in [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]:
        paths = create_paths(years = [year])
        deduper = Deduper(batch_size=2**19, num_minhashes=64)
        dedupe_path_ = os.path.join(dedupe_path, f"{year}")
        text_gen = create_text_gen(already_checked=set(), paths=paths)

        deduper.deduplicate(text_gen, return_generator=False, 
            overwrite=False,
            store_corpus_to_disk = False, 
            store_mask_to_disk = True, store_lsh_cache_to_disk = False, store_config_to_disk = False, output_dir=dedupe_path_)

        # print metadata
        mem_usage = psutil.virtual_memory()
        print('- RAM memory % used:', mem_usage[2])
        print('- Total memory used', bytes2human(mem_usage.used))



if __name__ == "__main__":
    dedupe_path = os.path.join("/work", "netarkivet-cleaned", "deduplicated")
    main(dedupe_path)
