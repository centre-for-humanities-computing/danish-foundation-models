'''
Filtering infomedia records that have 'Information', 'Inormation', 'Information (Papermill)' in the field of 'source'.
'''
import gzip
import json
from tqdm import tqdm

def process_records(chunk, filter_source):
    """
    Process a batch of records, filtering out records based on the 'source' field.
    """
    return [record for record in chunk if record.get('source') not in filter_source]

def read_and_filter_stream(input_json_gz, output_json_gz, filter_source=['Information', 'Inormation', 'Information (Papermill)'], batch_size=500):
    """
    Read a .json.gz file containing a JSON array and filter records,
    writing the filtered records to a new .json.gz file.
    """
    print('Loading the JSON array...')
    with gzip.open(input_json_gz, 'rt', encoding='utf-8') as f:
        data = json.load(f)  # Load the entire JSON array into memory

    filtered_data = []
    print('Start filtering...')
    # Process data sequentially in chunks
    total_chunks = (len(data) + batch_size - 1) // batch_size
    for i in tqdm(range(total_chunks)):
        start_idx = i * batch_size
        end_idx = start_idx + batch_size
        chunk = data[start_idx:end_idx]
        filtered_chunk = process_records(chunk, filter_source)
        filtered_data.extend(filtered_chunk)
    print('Done!')
    print(f'Now we have {len(filtered_data)} records after filtering.')
    # Write the filtered data back to a new .json.gz file
    print('Start writing json.gz file...')
    with gzip.open(output_json_gz, 'wt', encoding='utf-8') as f_out:
        json.dump(filtered_data, f_out)

def main():
    input_json_gz = '/work/dfm-data/pre-training/danews2.0/articles.json.gz'
    output_json_gz = '/work/dfm-data/pre-training/danews2.0/filtered_articles.json.gz'
    read_and_filter_stream(input_json_gz, output_json_gz)

if __name__ == '__main__':
    main()
