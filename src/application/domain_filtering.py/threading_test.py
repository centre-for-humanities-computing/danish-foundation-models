import concurrent.futures
import requests
import threading
import time

import os
import json
import pickle

from typing import Iterable
from itertools import islice

path = os.path.join(
    "/Users/au561649/Desktop/Github/danish-foundation-models/src/application/domain_filtering.py/safe_search_domains.json"
)

DNS = "cleanweb"  # normal (e.g. 8.8.8.8) or cleanweb (e.g. 185.228.168.10)

save_path = os.path.join(
    "/Users/au561649/Desktop/Github/danish-foundation-models/src/application/domain_filtering.py/safe_search_domains_safe_threaded.pkl"
)

if os.path.isfile(save_path):
    with open(save_path, "rb") as f:
        output = pickle.load(f)
    checked = set(output[DNS].values())
else:
    output = {}
    output["cleanweb"] = {}
    output["normal"] = {}
    checked = set()


def get_domains():
    with open(path, "r") as f:
        ss_domains = json.load(f)
    return ["http://" + d for d in ss_domains["false"] if d not in checked]


thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def download_site(url):
    session = get_session()
    try:
        with session.get(url, timeout=3) as response:
            return response.status_code
    except Exception as e:
        return e


def download_all_sites(sites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        return executor.map(download_site, sites)


def batch(dataset: Iterable, batch_size: int) -> Iterable:
    """Creates batches from an iterable.

    Args:
        dataset (Iterable): Your dataset you want to batch given as an iterable (e.g. a list).
        batch_size (int): Your desired batch size

    Returns:
        Iterable: An iterable of tuples of size equal to batch_size.

    Example:
        >>> batches = batch([1,2, 3, 4, 5], 2)
        >>> print(list(batches))
        [(1, 2), (3, 4), (5,)]
    """

    iterable_dataset = iter(dataset)
    while True:
        chunk = tuple(islice(iterable_dataset, batch_size))
        if not chunk:
            break
        yield chunk


if __name__ == "__main__":
    for i, sites in enumerate(batch(get_domains(), 500)):
        print(i)
        start_time = time.time()
        t = list(download_all_sites(sites))
        duration = time.time() - start_time
        print(f"\tDownloaded {len(sites)} sites in {duration} seconds")

        # append to output pickle
        for d, status in zip(sites, t):
            output[DNS][d] = isinstance(status, tuple)

        l = [isinstance(d, int) for d in output[DNS]]
        print(sum(l))
        print(len(l))

        with open(save_path, "wb") as f:
            pickle.dump(output, f)
    print("done")
