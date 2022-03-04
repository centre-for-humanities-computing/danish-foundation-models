import json
import os
from pysafebrowsing import SafeBrowsing

read_path = os.path.join("/work", "netarkivet-cleaned")
previous_lookups = os.path.join(read_path, "safe_search_domains.json")
API_key_path = os.path.join("/work", "ucloud-setup", "google_safe_search_api_token.txt")
with open(API_key_path, "r") as f:
    key = f.read()
safebrowse = SafeBrowsing(key)
r = safebrowse.lookup_urls(
    [
        "www.sexymotherfucker.dk",
        "sexologi.blogspot.com",
        "www.rudisexpresspizza-6440.dk",
        "www.stopsexturisme.dk",
        "www.sexogsanser.dk",
        "www.sexabc.dk",
        "www.sexnovellen.dk",
        "www.sex-erotik-porno.dk",
        "www.parterapi-sexolog.dk",
        "www.sexitoy.dk",
        "www.sexbase.dk",
        "www.sex-toy.dk",
        "www.xn--sexlegetj-shop-xqb.dk",
        "www.bisex.dk",
        "www.handicapsex.dk",
        "www.sexdiscount.dk",
    ]
)
API_key_path = os.path.join("/work", "ucloud-setup", "google_safe_search_api_token.txt")

with open(previous_lookups, "r") as f:
    prev = json.load(f)
