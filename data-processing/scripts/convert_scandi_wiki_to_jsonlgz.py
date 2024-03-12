"""
Convert jsonl files in tarfile from this format:

{
    "id": "...",
    "url": "...",
    "title": "...",
    "text": "...",
}

To this format:
{
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "foo",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp we acquired this data (time file was created), specified as YYYY-MM-DDTHH:MM:SS.TIMEZONE e.g 2021-04-13T12:52:46.000Z
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available), should be specified as a range; "YYYY-MM-DDTHH:MM:SS.TIMEZONE, YYYY-MM-DDTHH:MM:SS.TIMEZONE"
    "metadata": {            # OPTIONAL: source-specific metadata
        "sub-source": "...", # OPTIONAL: E.g. "newspaper_ocr"
        ...
    }
}

"""

import datetime
import gzip
import json
from pathlib import Path
import tarfile

def main():
    input_dir = Path("/directory-with-scandi-wiki.tar.gz-inside/")
    output_dir = Path("scandi-wiki")
    time_added = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    wiki_created = "2001-01-15T00:00:00.000Z"
    with tarfile.open(input_dir / "scandi-wiki.tar.gz") as tarf:
        for member in tarf.getmembers():
            if member.isfile() and member.name.endswith("jsonl"):
                output_path = output_dir / (Path(member.name).name + ".gz")
                if output_path.exists():
                    raise FileExistsError(f"{output_path} already exists")
                with gzip.open(output_path, "wt") as outfile:
                    iobytes = tarf.extractfile(member)
                    assert iobytes is not None
                    for line in iobytes:
                        assert line is not None
                        entry = json.loads(line)
                        output_entry = {
                            "id": entry["id"],
                            "text": entry["text"],
                            "source": "scandi-wiki",
                            "added": time_added,
                            "created": wiki_created + "," + time_added,
                            "metadata": {"url": entry["url"], "title": entry["title"], "language": Path(member.name).stem}
                        }
                        json.dump(output_entry, outfile)
                        outfile.write("\n")


if __name__ == "__main__":
    main()
