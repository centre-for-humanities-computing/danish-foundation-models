
from datasets import load_dataset
from pathlib import Path
import glob
from collections import Counter
import json
from wasabi import msg


domains = set()
lang_sites = Counter()
n_filtered = 0 
n_passed_quality_filter = 0
n_tokens = 0
n_sites = 0
n_tokens_clean = 0
n_not_duplicates = 0

def split_mask(mask, year_file):
    current_year = None
    current_file_id = None
    is_duplicate = []

    for mask_ in iter(mask):
        year, file_id, _ = mask_["id"].split("_")
        year, file_id = int(year), int(file_id)
        assert year == year_file

        if current_file_id is None:
            current_file_id = file_id
        if current_file_id != file_id:
            yield current_file_id, is_duplicate
            current_file_id = file_id
            is_duplicate = []
        
        is_duplicate.append(mask_["duplicate"])
    yield current_file_id, is_duplicate

for year in range(2006, 2017):
    msg.info(f"Processing year: {year}")
    path = f"/work/netarkivet-cleaned/{year}/*.jsonl_meta.csv"
    files = glob.glob(path)

    mask = load_dataset("json", data_files=f"/work/netarkivet-cleaned/deduplicated/{year}/mask.jsonl", streaming=True)
    mask = mask["train"]
    mask_gen = split_mask(mask, year)
    files = sorted(files, key=lambda file: int(file.split("/")[-1].split(".")[0]))
    
    for f in files:
        write = True
        file_id = int(f.split("/")[-1].split(".")[0])
        msg.info(f"\tfile_id: {file_id}")
        
        id_, mask_ = next(mask_gen)

        assert file_id == id_, "file id of file does not match mask"

        ds = load_dataset("csv", data_files=f)
        ds = ds["train"]
        iter_mask = iter(mask_)
        if "is_duplicate" in ds.features:
            write = False
        else:
            ds = ds.add_column("is_duplicate", [next(iter_mask) if passed is True else None for passed in ds["passed_quality_filter"]])

        domains_ = set(ds["domain_key"])
        domains.update(domains_)
        lang_sites += Counter(ds["language"])
        n_passed_quality_filter_ = len([i for i in ds["passed_quality_filter"] if i is True])
        n_passed_quality_filter +=n_passed_quality_filter_
        n_tokens += sum(ds["n_tokens"])
        n_sites += len(ds)
        n_clean_tokens_ = [n_tokens for n_tokens, is_dup in zip(ds["n_tokens"], ds["is_duplicate"]) if is_dup is False]
        n_not_duplicates += len(n_clean_tokens_)
        n_tokens_clean += sum(n_clean_tokens_)
        

        assert len(mask_) == n_passed_quality_filter_, "number of deduplicated files does not match n_passed_quality_filter_"

        if write:
            ds.to_csv(f)


save_path = "/work/netarkivet-cleaned/info.json"

msg.info(f"Writing json to {save_path}")
data = {"unique_domains": list(domains),
"language_site_counts": dict(lang_sites),
"n_quality_filtered_sites": lang_sites["da"],
"n_passed_quality_filtered_sites": n_passed_quality_filter,
"n_sites": n_sites,
"n_tokens_clean": n_tokens_clean,
"n_not_duplicates": n_not_duplicates
}


with open("/work/netarkivet-cleaned/info.json", "w") as f:
    json.dump(data, f)


msg.good(f"Finished. The following report some relevant statistics:")

p = f"""
NAT contains a total of {n_sites} sites. Over {len(domains)} domains
of which {lang_sites["da"]} is Danish,  {lang_sites["en"]} is English.

The Danish sites were quality filtered and {n_passed_quality_filter} ({n_passed_quality_filter/lang_sites["da"]:.2f}%)
passed the quality filter.

The sites which passed the quality filter were deduplicated pr. year
 and {n_not_duplicates} ({n_not_duplicates/n_passed_quality_filter:.2f}%) sites were left after the deduplication.

NAT consist of {n_tokens} of which {n_tokens_clean} ({n_tokens_clean/n_tokens:.2f}%) were left after quality
filtering and deduplication.
"""

print(p)

with open("/work/netarkivet-cleaned/info.txt", "w") as f:
    json.dump(p, f)