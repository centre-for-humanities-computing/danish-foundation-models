import csv
import datetime
import gzip
import io
import json
from pathlib import Path
import tarfile
import sys
from zoneinfo import ZoneInfo

def convert_file(input_path: Path, output_dir: Path):
    added_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    with tarfile.open(input_path, "r") as tarf:
        for member in tarf.getmembers():
            iobytes = tarf.extractfile(member)
            assert iobytes is not None
            iotext = io.TextIOWrapper(iobytes, encoding="latin1", newline="")
            with gzip.open(output_dir / (Path(member.name).stem + ".jsonl.gz"), "wt") as outf:
                reader = csv.DictReader(iotext)
                for i, row in enumerate(reader):
                    tz = ZoneInfo("Europe/Copenhagen")
                    created_date = datetime.datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
                    tz_name = tz.tzname(created_date) or ""
                    created_date_str = created_date.strftime("%Y-%m-%dT%H:%M:%S.000") + tz_name
                    new_obj = {
                        "id": str(i),
                        "text": row["text"],
                        "added": added_time,
                        "created": created_date_str,
                        "metadata": {
                            "platform": row["platform"],
                            "account": row["account"],
                            "url": row["url"],
                            "action": row["action"],
                        }
                    }
                    json.dump(new_obj, outf)
                    outf.write("\n")

def main():
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    convert_file(input_path, output_path)

if __name__ == "__main__":
    main()
