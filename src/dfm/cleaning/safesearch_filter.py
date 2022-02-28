from typing import Iterable, List, Set
from googlesearch import search, get_random_user_agent
from urllib.parse import urlparse
import urllib
from collections import Counter

import numpy as np

from search import search



def gen_wait_time():
    wait = np.random.normal(2, 1)
    if wait < 1:
        return 1
    if wait > 4:
        return 4
    return wait


def google_search_filter(domains: List[str], n: int = 10, lang="da") -> Set[str]:
    """Takes a list of domains and performs a google safe search for extract

    Args:
        domains (Iterable[str]): A list of domains you wish to extract unsafe domains from

    Returns:
        Set[str]: Domains considered unsafe by google safesearch
    """

    def get_domain(url: str):
        return urlparse(url).netloc

    n_safe_on = Counter()
    n_safe_off = Counter()
    while domains:
        domain = domains.pop()
        # try:
        for url in search(domain, num=n, stop=n, lang=lang, pause=gen_wait_time()):
            n_safe_off[get_domain(url)] += 1
        for url in search(
            domain, num=n, stop=n, lang=lang, safe="on", pause=gen_wait_time()
        ):
            n_safe_on[get_domain(url)] += 1
        # except urllib.error.HTTPError:

    return n_safe_on, n_safe_off


if __name__ == "__main__":

    with open("src/dfm/cleaning/unsafe_domains_test.txt", "r") as f:
        domains = f.read().split("\n")
    safe, unsafe = google_search_filter(domains, lang="en")

    unsafe.most_common(10)
