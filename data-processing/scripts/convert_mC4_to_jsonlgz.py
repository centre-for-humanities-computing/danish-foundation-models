""" Preprocess Danish subset of the mC4 3.1.0 dataset.
    To download the required data, run the following commands:

    GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/datasets/allenai/c4
    cd c4
    git lfs install
    git lfs pull --include "multilingual/c4-da.*.json.gz"
"""
from pathlib import Path
import datetime
import jsonlines
import multiprocessing
import functools
import sys
import gzip
import os

### Dataformat expected for Dolma
###{
###    "id": "...",             # MANDATORY: source-specific identifier
###    "text": "foo",           # MANDATORY: textual content of the document
###    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
###    "added": "...",          # OPTIONAL: timestamp ai2 acquired this data
###    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available)
###    "metadata": {...}        # OPTIONAL: source-specific metadata
###}

timenow = datetime.datetime.now().strftime("%Y-%m-%d"),

def process_single(filepath: Path, source_dir: Path, output_dir: Path):
    relname = filepath.relative_to(source_dir)
    output_file = output_dir / relname

    document_idx = 0
    with gzip.open(filepath, "rt", encoding="UTF-8") as infile, gzip.open(output_file, "wt", encoding="UTF-8") as outfile:
        with jsonlines.Writer(outfile) as writer:
            for doc in jsonlines.Reader(infile):
                created = datetime.datetime.strptime(doc["timestamp"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                formatted_doc = {}
                formatted_doc["id"] = str(relname).replace(os.path.sep, "--") + "_" + str(document_idx)
                formatted_doc["text"] = doc["text"]
                # formatted_doc["source"] = "c4-da"
                formatted_doc["source"] = "mC4"
                formatted_doc["created"] = created + ", " + created
                formatted_doc["added"] = timenow
                formatted_doc["metadata"] = {key: doc[key] for key in doc.keys() if key not in ["text", "timestamp"]}

                writer.write(formatted_doc)

                document_idx += 1

def main():
    source_dir = Path(sys.argv[1]) # c4/multilingual
    output_dir = Path(sys.argv[2])
    for lang in ["da", "sv", "no", "is"]:
        file_paths = sorted(
            source_dir.glob(f"c4-{lang}.*.json.gz")
        )

        mapfunc = functools.partial(process_single, source_dir=source_dir, output_dir=output_dir)
        print(f"Processing {len(file_paths)} files.")
        with multiprocessing.Pool(processes=12) as pool:
            pool.map(mapfunc, file_paths)

if __name__ == "__main__":
    main()
