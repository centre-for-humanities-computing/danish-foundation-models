"""
sudo networksetup -setdnsservers Wi-Fi 185.228.168.10
sudo networksetup -setdnsservers Wi-Fi 8.8.8.8
"""
import json
import os
import socket


def _getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return socket.getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


def dns_lookup(host):
    try:
        _getaddrinfo(host, 80)
    except socket.gaierror:
        return host, False
    return host, True


path = os.path.join(
    "/Users/au561649/Desktop/Github/danish-foundation-models/src/application/domain_filtering.py/safe_search_domains.json"
)

with open(path, "r") as f:
    ss_domains = json.load(f)

valid_dom = {}
valid_dom["safesearch_malicious"] = ss_domains["true"]
valid_dom["safesearch_not_malicious"] = ss_domains["false"]


host1 = "http://www.pornhub.com"
host2 = "http://www.google.com"






def dns_lookup_system(host):
    try:
        return requests.head("http://" + host)
    except Exception as e:
        return e



import subprocess

from tqdm import tqdm
import multiprocessing as mp
import time
import requests
import concurrent.futures
import requests
import threading
if __name__ == "__main__":
    # s = time.time()
    # for i in ss_domains["false"][:1000]:
    #     try:
    #         output = subprocess.check_output(f"host -a {i} 8.8.8.8", shell=True)
    #     except:
    #         pass
    #     # t = os.system(f"host -a {i} 8.8.8.8")
    # e = time.time() - s
    # print(e)
    s = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(dns_lookup, ss_domains["false"][:3000])
    # with mp.Pool(16) as p:
    #     t = list(p.imap(dns_lookup_system, tqdm(ss_domains["false"][:3000])))

    e = time.time() - s
    print(e)

    t[0]

    # valid_dom["dns_lookup_8.8.8.8"] = {d: dns_lookup(d) for d in ss_domains["false"][:3000]}
    # s = time.time()
    # with mp.Pool(16) as p:
    #     t = p.map(dns_lookup, ss_domains["false"][:3000])
    # e = time.time()-s
    # print(e)

# valid_dom["dns_lookup_185.228.168.10"] = {d: dns_lookup(d) for d in tqdm(ss_domains["false"])}

# [d for d, valid in valid_dom["dns_lookup_185.228.168.10"].items() if not valid and valid_dom["dns_lookup_8.8.8.8"][d]]

# # med googles: 8.8.8.8
# print(dns_lookup("wowsucherror"))  # false
# print(dns_lookup("google.com"))  # true
# print(dns_lookup("www.pornhub.com"))  # true
# # med cleanbrowsing: 185.228.168.10
# print(dns_lookup("wowsucherror"))  # false
# print(dns_lookup("google.com"))  # true
# print(dns_lookup("www.pornhub.com"))  # false



