"""
Convert from collection of files in this format:

{
   "content":"English sentence\nphrase en français\n????????????", // (1)
   "warc_headers":{ // (2)
      "warc-identified-content-language":"fra,eng",
      "warc-target-uri":"https://fr.wikipedia.org/wiki/...",
      "warc-record-id":"<urn:uuid:29eaa920-d299-4b1d-b687-c72bd8d68116>",
      "warc-type":"conversion",
      "content-length":"35298", // (3)
      "warc-refers-to":"<urn:uuid:39e42055-0d94-4e45-9c6c-9e7056635d64>",
      "warc-block-digest":"sha1:WFH2A5WHCS2H365GIAFYQPI7UOAMFGHB", // (3)
      "warc-date":"2022-11-26T09:45:47Z",
      "content-type":"text/plain"
   },
   "metadata":{
      "identification":{ // (4)
         "label":"fr",
         "prob":0.8938327
      },
      "harmful_pp":4063.1814, // (5)
      "tlsh":"tlsh:T125315FF2B6088901EEA097015DB39B4600B...", // (6)
      "quality_warnings":[ // (7)
         "short_sentences",
         "header",
         "footer"
      ],
      "categories":[ // (8)
         "examen_pix",
         "liste_bu"
      ],
      "sentence_identifications":[ // (9)
         {
            "label":"fr",
            "prob":0.99837273
         },
         {
            "label":"en",
            "prob":0.9992377
         },
         null
      ]
   }
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
import io
import json
import multiprocessing
import sys
from pathlib import Path
from typing import Union, Any

import zstandard

DOCS_PER_FILE = 1000000

def process_one(output_dir: Path, root_path: Path, input_path: Path) -> None:
    doc_count = 0
    out_fh = None
    with input_path.open("rb") as in_fh:
        dctx = zstandard.ZstdDecompressor(max_window_size=2147483648)
        stream_reader = dctx.stream_reader(in_fh)
        text_stream = io.TextIOWrapper(stream_reader, encoding="utf-8")
        for line in text_stream:
            if (doc_count % DOCS_PER_FILE) == 0:
                # Convert relative path colossal-oscar-1.0/11-17/da_meta/da_meta_part_2.jsonl.zst
                # to output_path/11-17__da_meta__da_meta_part2_{idx}.jsonl.gz
                rel_input_path_parts = input_path.relative_to(root_path).parts
                output_path = output_dir / "__".join(rel_input_path_parts[:-1]) / (
                    Path(Path(rel_input_path_parts[-1]).stem).stem + f"_{doc_count//DOCS_PER_FILE}.jsonl.gz"
                )
                if out_fh is not None:
                    out_fh.close()
                out_fh = gzip.open(output_path, "wt")
            obj = json.loads(line)
            new_obj: dict[str, Union[dict[str, Any], str]] = {
                "id": str(obj["warc_headers"]["warc-record-id"]), # Copy metadata id to root
                "text": obj["content"],
                "source": "colossal_oscar_1.0",
                "added": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "created": obj["metadata"]["warc-date"], # Copy metadata to root
                "metadata": obj["metadata"],
            }
            new_obj["metadata"]["warc_headers"] = obj["warc_headers"] # type: ignore
            new_obj["metadata"]["url"] = obj["warc_headers"]["warc-target-uri"] # type: ignore

            assert out_fh is not None
            json.dump(new_obj, out_fh)
            doc_count += 1
            out_fh.write("\n")

def main():
    assert (
        len(sys.argv) == 3
    ), "Usage: convert_colossal_oscar_10_to_jsonlgz.py colossal_oscar_root output_directory"

    oscar_root_dir = Path(sys.argv[1])
    input_files = oscar_root_dir.glob("./**/da_meta/*.jsonl.zst")
    output_dir = Path(sys.argv[-1])

    with multiprocessing.Pool(processes=8) as pool:
        results = [
            pool.apply_async(process_one, (output_dir, oscar_root_dir, fname))
            for fname in input_files
        ]
        for res in results:
            res.get()


if __name__ == "__main__":
    main()
