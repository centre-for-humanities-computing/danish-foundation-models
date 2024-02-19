import os
import orjsonl
from collections import Counter
from pathlib import Path
from tqdm import tqdm
import argparse
from urllib.parse import urlparse
import csv

def count_domain_hits(input_path: Path):
    domain_counter = Counter()
    input_files = list(input_path.glob("*.jsonl.zst"))
    
    for input_file in tqdm(input_files, desc="Processing files"):
        lines = orjsonl.stream(input_file)
        for line in lines:
            if 'url' in line:
                domain = urlparse(line['url']).netloc
                domain_counter[domain] += len(line['text'])
                
    return domain_counter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count hits by domain in .jsonl.zst files.")
    parser.add_argument("--input_path", type=str, required=True, help="Path to the input directory containing .jsonl.zst files")
    args = parser.parse_args()

    input_path = Path(os.path.abspath(args.input_path))
    assert input_path.is_dir(), "Input path must be a directory"
    
    domain_counts = count_domain_hits(input_path)

    sum_counts = sum(domain_counts.values())
    print(f"Num characters: {sum_counts}")

    sorted_domain_counts = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    with open('domain_counts.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Domain', 'Count', 'Percent'])
        for domain, count in sorted_domain_counts:
            writer.writerow([domain, count, round(count / sum_counts * 100, 3)])
