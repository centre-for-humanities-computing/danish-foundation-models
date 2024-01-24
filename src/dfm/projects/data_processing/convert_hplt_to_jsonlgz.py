import datetime
import gzip
import io
import json
from pathlib import Path
import sys
import zstandard

def main():
    assert len(sys.argv) >= 3, "Usage: hplt_to_dolma_format.py f1.jsonl.zst f2.jsonl.zst ... output_directory"

    input_files = sys.argv[1:-1]
    output_dir = sys.argv[-1]

    for fname in input_files:
        input_path = Path(fname)
        output_path = Path(output_dir) / (input_path.stem + ".gz")
        with open(input_path, 'rb') as in_fh, gzip.open(output_path, 'wt') as out_fh:
            dctx = zstandard.ZstdDecompressor(max_window_size=2147483648)
            stream_reader = dctx.stream_reader(in_fh)
            text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')
            for line in text_stream:
                obj = json.loads(line)
                new_obj = {
                    "id": obj["id"],
                    "text": obj["text"],
                    "source": "hplt1.2",
                    "added": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                }
                for key, val in obj.items():
                    if key not in new_obj:
                        if "metadata" not in new_obj:
                            new_obj["metadata"] = {}
                        new_obj["metadata"][key] = val

                json.dump(new_obj, out_fh)
                out_fh.write("\n")

if __name__ == "__main__":
    main()
