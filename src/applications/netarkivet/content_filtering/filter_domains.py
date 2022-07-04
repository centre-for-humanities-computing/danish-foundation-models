"""
Filters domains from Netarkivet using Google Safe Browsing and a DNS filter

Dependent on:
    Assumed run after count_domains_netarkivet.py

Authors:
    Kenneth Enevoldsen
"""


import json
import os
from collections import Counter, defaultdict
from typing import List

from pysafebrowsing import SafeBrowsing
from wasabi import msg

from .count_domains import get_paths
from .DNS_filter import dns_filter

read_path = os.path.join("/work", "netarkivet-cleaned")
dfm_path = os.path.join("ucloud-setup", "githubs", "danish-foundation-models")
API_key_path = os.path.join("/work", "ucloud-setup", "google_safe_search_api_token.txt")
previous_lookups = os.path.join(read_path, "safe_search_domains.json")
daily_api_calls = 10_000


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


def main():
    # load in existing lookups if any
    if os.path.isfile(previous_lookups):
        with open(previous_lookups, "r") as f:
            prev = json.load(f)
    else:
        msg.warn("Did not find any previous lookups.")
        prev = {}

    already_checked = {d for k, dom in prev.items() for d in dom}

    safe_search = defaultdict(list)
    for k in prev:
        safe_search[k] = prev[k]

    msg.info(f"Loading in {len(already_checked)} checked domains")

    # combine counters with domains
    paths = get_paths(path=read_path, file_suffix="domain_counts.json", nested=False)
    counters = [read_counter_json(path) for path in paths]
    counter = sum_counters(counters)

    n_domains_entries = sum(counter.values())

    api_calls = daily_api_calls
    # remove singles
    domains = [(dom, count) for dom, count in counter.most_common() if count > 1]

    # load api key
    with open(API_key_path, "r") as f:
        key = f.read()
    safebrowse = SafeBrowsing(key)

    n = len(domains)
    msg.info(
        f"A total of  {len(counter)} unique domains and {n} unique domains with more"
        + " than one entry."
    )
    msg.info(
        f"There was a total of {n_domains_entries} entries and"
        + f" {n_domains_entries - sum([c for d,c in domains])}"
        + " were unique domain entries."
    )

    # call safe search API
    domains = [d for d, c in domains if d not in already_checked]
    start, end = 0, 0
    msg.info(f"Planning to make {len(range(500, n, 500))+1} API calls")

    for end in range(500, n, 500):  # max domains pr. call is 500
        domains_ = domains[start:end]
        api_calls -= 1
        r = safebrowse.lookup_urls(domains_)
        for dom, mal in r.items():
            safe_search[str(mal["malicious"]).lower()].append(dom)
        if api_calls <= 0:
            break
        start = end
    # handle the tail
    if domains[end:]:
        r = safebrowse.lookup_urls(domains[end:])
        for dom, mal in r.items():
            safe_search[str(mal["malicious"]).lower()].append(dom)

    msg.info(f"API calls left: {api_calls}")

    # write file
    with open(os.path.join(read_path, "safe_search_domains.json"), "w") as f:
        json.dump(safe_search, f)

    msg.good("Finished, printing sample of safe and unsafe domains:")
    for k in safe_search:
        print(k, ":", safe_search[k][:5])


if __name__ == "__main__":
    main()

    path = os.path.join("/work/netarkivet-cleaned/safe_search_domains.json")
    save_path = os.path.join("/work/netarkivet-cleaned/safe_search_domains_safe.pkl")
    dns_filter(cache_file=save_path)
