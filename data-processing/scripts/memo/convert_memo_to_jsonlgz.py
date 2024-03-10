'''
This script converts the dataset Memo
from .txt (text) & .csv(metadata) to json.gz:

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
'''

import pandas as pd
import json
import gzip
import os
from tqdm import tqdm
import datetime
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

def format_created_range(year):
    """Create a possible time period during which the file was created."""
    start_date = f"{year}-01-01T00:00:00.000Z"  # Start of the year
    end_year = int(year) + 100
    end_date = f"{end_year}-01-01T00:00:00.000Z"
    return f"{start_date}, {end_date}"

def convert_txt_and_metadata(metadata_path, txt_folder_path, output_path):
    """Construct a JSON.GZ for memo based on a folder of texts and a table of metadata, return the number of tokens as well."""
    # Load the metadata (.csv)
    metadata_df = pd.read_csv(metadata_path)

    num_tokens = 0

    # JSON.GZ
    with gzip.open(output_path, 'wt', encoding='utf-8') as gz_file:
        gz_file.write("[")
        
        first_record = True
        for _, row in tqdm(metadata_df.iterrows(), total=len(metadata_df), desc="Processing records"):
            # Note: filename in metadata has .pdf instead of .txt
            if pd.notna(row['filename']):
                filename = row['filename'].replace('.pdf', '') + '.txt'
            else:
                continue
            
            text_path = os.path.join(txt_folder_path, filename)
            if not os.path.exists(text_path):
                continue
            
            try:
                with open(text_path, 'r', encoding='utf-8') as txt_file:
                    text = txt_file.read()
            except Exception as e:
                print(f"Error reading file {text_path}: {e}")
                continue
            # Note: file_id is a string
            file_id = str(row['file_id']) if pd.notna(row['file_id']) else None
            added = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            created = format_created_range(row['year']) if pd.notna(row['year']) else "1870-01-01T00:00:00.000Z, 1970-01-01T00:00:00.000Z"
            
            # Count tokens
            num_tokens += len(word_tokenize(text))

            document = {
                "id": file_id,
                "text": text,
                "source": row['source'],
                "added": added,
                "created": created,
                "metadata": {field: row[field] for field in metadata_df.columns}
            }
            
            # Separate JSON objects with commas, except for the first one
            if not first_record:
                gz_file.write(",")
            else:
                first_record = False
            
            gz_file.write(json.dumps(document))
        
        gz_file.write("]")

    print("Dataset processing completed.")
    # 64978441 tokens in total.
    print(f"{num_tokens} tokens in total.")
    
    return num_tokens

def main():
    """Specify input and output paths."""
    metadata_path = '/work/github/Corpus-v1.1/MeMo-corpus-metadata-v1.1-2023-06-20.csv'

    # The folder containing all the normalized TXT files
    txt_folder_path = '/work/github/Corpus-v1.1/normalized'

    output_path = '/work/dfm-data/pre-training/memo/normalized_memo.json.gz'
    
    convert_txt_and_metadata(metadata_path, txt_folder_path, output_path)

if __name__ == "__main__":
    main()
