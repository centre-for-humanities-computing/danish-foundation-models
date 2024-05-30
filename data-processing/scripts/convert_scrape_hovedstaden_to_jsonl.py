"""
Scrape from document collection at Vip Region Hovedstaden:
https://sprogteknologi.dk/dataset/1076892a-14ee-4f14-a9db-32efb03c40c9
"""
import os
import json
import gzip
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import tqdm

def process_file(file_path):
    try:
        # added_timestamp = datetime.utcfromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d')
        added_timestamp = datetime.now().strftime('%Y-%m-%d')
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()

        json_object = {
            "id": f"doc_hovedstaden_{os.path.splitext(os.path.basename(file_path))[0]}",
            "text": text_content,
            "source": "scrape_hovedstaden",
            "added": added_timestamp,
            "created": "2023-11-16, 2024-04-04",
            "metadata": {
                "subject": "health",
                "language": "danish",
                "organization": "The Danish Agency for Digitalisation",
                "source-pretty": "University of Southern Denmark (SDU) & Capital Region",
                "URL": "https://sprogteknologi.dk/dataset/1076892a-14ee-4f14-a9db-32efb03c40c9"
            }
        }

        return json_object
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def convert_txt_to_jsonl_gz(directory, output_file):
    files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.txt')]
    futures = []

    # Start processing files in parallel
    with ProcessPoolExecutor() as executor:
        for file_path in files:
            future = executor.submit(process_file, file_path)
            futures.append(future)
        
        results = []
        for future in tqdm.tqdm(as_completed(futures), total=len(futures), desc="Processing files"):
            results.append(future.result())

    results = [result for result in results if result is not None]

    with gzip.open(output_file, 'wt', encoding='utf-8') as gz_file:
        for item in results:
            gz_file.write(json.dumps(item) + '\n')

    print(f"Output saved to {output_file}")

def main():
    directory = '/work/github/capital_region/korpus/renset'
    output_file = '/work/dfm-data/pre-training/scrape_hovedstaden/documents/scrape_hovedstaden.jsonl.gz'
    convert_txt_to_jsonl_gz(directory, output_file)

if __name__ == '__main__':
    main()
