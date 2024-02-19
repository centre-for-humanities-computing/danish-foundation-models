import os
import sys
import orjsonl
from pathlib import Path
import itertools

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    shard_size = int(sys.argv[3])

    input_files = list(Path(input_dir).glob("*.jsonl.zst"))
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    current_shard = 0
    lines = itertools.chain.from_iterable(orjsonl.stream(input_file) for input_file in input_files)
    while True:
        output_file = os.path.join(output_dir, f"shard{current_shard}.jsonl.zst")
        print(f"Writing {output_file}...")
        slines = list(itertools.islice(lines, shard_size))
        orjsonl.save(output_file, slines)
        if len(slines) < shard_size:
            break
        current_shard += 1
