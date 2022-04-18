from typing import Iterable

import glob
import os
import sys
from pathlib import Path
from functools import partial

from tqdm import tqdm
from wasabi import msg
import ndjson


dfm_path = Path("danish-foundation-models")
sys.path.append(dfm_path)


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
                    yield website


def main() -> None:
    write_folder = Path("netarkivet-cleaned")

    # [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]:
    for year in [2014, 2015, 2016]:
        paths = create_paths(years = [year])
        text_gen = create_text_gen(already_checked=set(), paths=paths)

        path = write_folder / f"{year}_is_valid.ndjson"
        with open(path, "w") as f:
            writer = ndjson.writer(f, ensure_ascii=False)

            for text in text_gen:
                writer.writerow(text)

if __name__ == "__main__":
    main()
