import datetime
import gzip
import io
import json
from pathlib import Path
import tarfile
import sys

def convert_file(input_path: Path, output_dir: Path):
    added_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    created_date_str = "2017-01-01T00:00:00.000Z, 2024-01-01T00:00:00.000Z"
    with tarfile.open(input_path, "r") as tarf:
        for member in tarf.getmembers():
            iobytes = tarf.extractfile(member)
            assert iobytes is not None
            iotext = io.TextIOWrapper(iobytes, encoding="utf8")
            # Loop over texts until we get to a "mødet er åbnet" and then save to output
            with gzip.open(output_dir / (Path(member.name).stem + ".jsonl.gz"), "wt") as outf:
                speech_idx = 0
                text = ""
                for line in iotext:
                    if "mødet er åbnet" in line and len(text) > 0:
                        new_obj = {
                            "id": str(speech_idx),
                            "text": text,
                            "added": added_time,
                            "created": created_date_str,
                        }
                        json.dump(new_obj, outf)
                        outf.write("\n")

                        speech_idx += 1
                        text = line
                    else:
                        text = text + line

def main():
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    convert_file(input_path, output_path)

if __name__ == "__main__":
    main()
