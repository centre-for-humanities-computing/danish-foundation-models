from collections import Counter
from typing import Any, Optional
from pathlib import Path
import sys

import smart_open
import msgspec
from msgspec import Struct
import urllib3.util

class DocumentWithMetadata(Struct):
    id: str
    text: str
    metadata: Optional[dict[str, Any]] = None
    attributes: Optional[dict[str, Any]] = None

def counter_to_csv(counter: Counter, csv_file: Path):
    total = counter.total()
    with open(csv_file, "w") as f:
        for url, count in counter.most_common():
            f.write(f"{url},{count},{(100*count)/total}\n")

def main():

    url_counter_docs: Counter[str] = Counter()
    url_counter_characters: Counter[str] = Counter()
    decoder = msgspec.json.Decoder(DocumentWithMetadata)
    outfile_docs = Path("url_count_docs.csv")
    outfile_characters = Path("url_count_characters.csv")

    for path in sys.argv[1:]:
        fpath = Path(path)
        print(fpath)

        with smart_open.open(fpath) as f:
            for ln in f:
                try:
                    row = decoder.decode(ln)
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to decode line {ln} in {fpath}; "
                    ) from e
                if len(row.text) > 0:
                    assert row.metadata is not None
                    url: str = row.metadata["url"]
                    parsed_url = urllib3.util.parse_url(url)
                    if parsed_url.host is not None:
                        url_counter_docs[parsed_url.host] += 1
                        url_counter_characters[parsed_url.host] += len(row.text)

    counter_to_csv(url_counter_docs, outfile_docs)
    counter_to_csv(url_counter_characters, outfile_characters)

if __name__ == "__main__":
    main()







