import datetime
import gzip
import io
import json
from pathlib import Path
import sys
import zstandard
import multiprocessing

DOCS_PER_FILE=1000000
#DOCS_PER_FILE=1000

def process_one(output_dir, input_path):
    doc_count = 0
    out_fh = None
    with open(input_path, 'rb') as in_fh:
        dctx = zstandard.ZstdDecompressor(max_window_size=2147483648)
        stream_reader = dctx.stream_reader(in_fh)
        text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')
        for line in text_stream:
            if (doc_count % DOCS_PER_FILE) == 0:
                output_path = Path(output_dir) / (Path(input_path.stem).stem + f"_{doc_count//DOCS_PER_FILE}.jsonl.gz")
                if out_fh is not None:
                    out_fh.close()
                out_fh = gzip.open(output_path, 'wt')
            obj = json.loads(line)
            new_obj = {
                "id": str(obj["id"]),
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
            doc_count += 1
            out_fh.write("\n")
    return True

def main():
    assert len(sys.argv) >= 3, "Usage: hplt_to_dolma_format.py f1.jsonl.zst f2.jsonl.zst ... output_directory"

    input_files = sys.argv[1:-1]
    output_dir = sys.argv[-1]

    with multiprocessing.Pool(processes=2) as pool:
        results = [pool.apply_async(process_one, (output_dir, Path(fname))) for fname in input_files]
        for res in results:
            res.get()


if __name__ == "__main__":
    main()
