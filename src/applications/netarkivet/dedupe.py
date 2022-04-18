"""
Applies quality filters to Netarkivet filtering based on language tags.

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen

"""
from memory_profiler import profile

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


dfm_path = os.path.join("danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import Deduper
from src.dfm.utils import batch


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


fp=open('memory_profiler_main.log','w+')

@profile(stream=fp)
def main(
    dedupe_path: str,
) -> None:
    # [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]:
    for n_hash, split_method in [(64, "paragraph"), 
                                #(64, "word_ngram"), (16, "word_ngram"), (32, "word_ngram")
                                ]:
        for year in [2014]:
            # paths = create_paths(years = [year])
            paths = [(0, year, "/work/netarkivet-cleaned/2014_test.jsonl"), (1, year, "/work/netarkivet-cleaned/2014_test2.jsonl")]
            for i, batch_paths in enumerate(batch(paths, batch_size=10)):
                deduper = Deduper(batch_size=2**19, num_minhashes=n_hash, split_method=split_method)
                dedupe_path_ = os.path.join(dedupe_path, f"{year}_b{i}")
                text_gen = create_text_gen(already_checked=set(), paths=batch_paths)

                deduper.deduplicate(text_gen, return_generator=False, 
                    overwrite=True, # TODO CHANGE TO FALSE
                    store_corpus_to_disk = False, 
                    store_mask_to_disk = True, store_lsh_cache_to_disk = False, store_config_to_disk = False, output_dir=dedupe_path_)

                import psutil  
                from psutil._common import bytes2human
                mem_usage = psutil.virtual_memory()
                print('- RAM memory % used:', mem_usage[2])
                print('- Total memory used', bytes2human(mem_usage.used))
                print(n_hash, split_method)
                # Getting % usage of virtual_memory ( 3rd field)
                # deduper.save_to_disk(output_dir=dedupe_path_, overwrite=True)



if __name__ == "__main__":
    dedupe_path = os.path.join("/work", "netarkivet-cleaned", "deduplicated")
    main(dedupe_path)
