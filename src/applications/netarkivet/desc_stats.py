"""
Combines counter derived from count_domains_netarkivet.py to create descriptive statistic from netarkivet.

Author:
    Kenneth Enevoldsen


Dependent on:
    count_domains_netarkivet.py 
"""
from typing import List

import os
import sys
import json
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

dfm_path = os.path.join("/work", "danish-foundation-models")

sys.path.append(dfm_path)

from src.applications.netarkivet.content_filtering.count_domains_netarkivet import (
    get_paths,
)


def sum_counters(counters: List[Counter]) -> Counter:
    """
    Recursive counter with a O(log(n)) Complexity
    """
    length = len(counters)
    if length > 10:
        c1 = sum_counters(counters[: int(length / 2)])
        c2 = sum_counters(counters[int(length / 2) :])
        return sum([c1, c2], Counter())
    else:
        return sum(counters, Counter())


def read_counter_json(path):
    """read jsons consisting of multiple counters in as one counter"""
    with open(path, "r") as f:
        c = json.load(f)
    return sum_counters([Counter(counts) for counts in c])


def main(read_path: str):
    save_path = "/work/danish-foundation-models/docs/desc_stats"

    print("Starting domains")
    # Domains
    #   read in and combine counters
    paths = get_paths(path=read_path, file_suffix="domain_counts.json", nested=False)
    d_counters = [read_counter_json(path) for path in paths]
    d_counter = sum_counters(d_counters)

    #   write desc stats
    df = pd.DataFrame.from_dict(d_counter, orient="index").reset_index()
    df.to_csv(os.path.join(save_path, "domain_counts.csv"))

    print("Starting time stamp")
    # Time stamps
    #   read in and combine counters
    paths = get_paths(path=read_path, file_suffix="timestamp_counts.json", nested=False)
    t_counters = [read_counter_json(path) for path in paths]
    t_counter = sum_counters(t_counters)

    #   write desc stats
    df = pd.DataFrame.from_dict(t_counter, orient="index").reset_index()
    df.to_csv(os.path.join(save_path, "timestamp_counts.csv"))

    print("Done")


if __name__ == "__main__":
    read_path = os.path.join("/work", "netarkivet-cleaned")
    main(read_path)
