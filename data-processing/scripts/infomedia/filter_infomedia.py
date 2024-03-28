'''
Filtering infomedia records that have 'Information', 'Inormation', 'Information (Papermill)' in the field of 'source'.
'''
import gzip
import json

def read_and_filter_stream(input_jsonl_gz, output_jsonl_gz, filter_source=['Information', 'Inormation', 'Information (Papermill)'], batch_size=500):
    """
    Read a .jsonl.gz file and filter records,
    writing the filtered records to a new .jsonl.gz file.
    """
    print('Filtering the JSONL file...')
    with gzip.open(input_jsonl_gz, 'rt', encoding='utf-8') as infile,\
        gzip.open(output_jsonl_gz, 'wt', encoding='utf-8') as outfile:
        for line in infile:
            record = json.loads(line)
            if record.get('source') not in filter_source:
                json.dump(record, outfile)
                outfile.write('\n')
    print('Done!')

def main():
    input_jsonl_gz = '/work/dfm-data/pre-training/danews2.0/articles.jsonl.gz'
    output_jsonl_gz = '/work/dfm-data/pre-training/danews2.0/filtered_articles.jsonl.gz'
    read_and_filter_stream(input_jsonl_gz, output_jsonl_gz)

if __name__ == '__main__':
    main()
