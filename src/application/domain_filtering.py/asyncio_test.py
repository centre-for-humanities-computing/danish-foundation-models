"""
pip install asyncio aiohttp
"""
from typing import Iterable
from itertools import islice
import asyncio
import json
import os
import pickle
import time

import aiohttp
from aiohttp import ClientTimeout

from concurrent.futures import ThreadPoolExecutor

path = os.path.join(
    "/Users/au561649/Desktop/Github/danish-foundation-models/src/application/domain_filtering.py/safe_search_domains.json"
)

DNS = "cleanweb"  # normal (e.g. 8.8.8.8) or cleanweb (e.g. 185.228.168.10)

save_path = os.path.join(
    "/Users/au561649/Desktop/Github/danish-foundation-models/src/application/domain_filtering.py/safe_search_domains_safe.pkl"
)

if os.path.isfile(save_path):
    with open(save_path, "rb") as f:
        output = pickle.load(f)
    checked = set(output[DNS].keys())
else:
    output = {}
    output["cleanweb"] = {}
    output["normal"] = {}
    checked = set()


def get_domains():
    with open(path, "r") as f:
        ss_domains = json.load(f)
    return ["http://" + d for d in ss_domains["false"] if d not in checked]


async def download_site(session, url):
    async with session.get(
        url, timeout=ClientTimeout(total=None, sock_connect=5, sock_read=5)
    ) as response:
        code = response.status
    return url, code


async def download_all_sites(sites):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in sites:
            task = asyncio.create_task(download_site(session, url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    return responses


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
    for i, sites in enumerate(batch(get_domains(), 1000)):
        # 200 : 62timer (11, 11, 100, 150)
        # # 300 107 timer #
        print(i)
        start_time = time.time()
        loop = asyncio.get_event_loop()
        loop.set_default_executor(ThreadPoolExecutor(1000))
        t = loop.run_until_complete(download_all_sites(sites))

        duration = time.time() - start_time
        print(f"\tDownloaded {len(sites)} sites in {duration} seconds")

        # append to output pickle
        for d, status in zip(sites, t):
            output[DNS][d] = isinstance(status, tuple)

        # l = [d for d in output[DNS]]
        # print(sum(l))
        # print(len(l))
        with open(save_path, "wb") as f:
            pickle.dump(output, f)
        print("done")
