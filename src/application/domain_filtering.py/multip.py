# Multiprocessing (takes way too long for 5 domains)


import requests
import multiprocessing
import time

import os
import json

path = os.path.join(
    "/Users/au561649/Desktop/Github/danish-foundation-models/src/application/domain_filtering.py/safe_search_domains.json"
)


def get_domains():
    with open(path, "r") as f:
        ss_domains = json.load(f)

    return ["http://" + d for d in ss_domains["false"]]


session = None


def set_global_session():
    global session
    if not session:
        session = requests.Session()


def download_site(url):
    with session.head(url) as h:
        name = multiprocessing.current_process().name
        print(f"{name}:Read {len(h)} from {url}")


def download_all_sites(sites):
    with multiprocessing.Pool(initializer=set_global_session) as pool:
        pool.map(download_site, sites)


if __name__ == "__main__":
    sites = get_domains()[:5]  # only a subset
    start_time = time.time()
    download_all_sites(sites)
    duration = time.time() - start_time
    print(f"Downloaded {len(sites)} in {duration} seconds")
