"""
Construct jsonl.gz from text files and metadata csv with NaN handling.
"""
import pandas as pd
import json
import gzip
import os
from tqdm import tqdm
import datetime
import uuid
import nltk # type: ignore
from nltk.tokenize import word_tokenize # type: ignore

# Ensure nltk punkt tokenizer models are downloaded
nltk.download('punkt', quiet=True)

def clean_nested_dict(obj):
    """Recursively replaces NaN values and converts non-serializable objects to None."""
    if isinstance(obj, dict):
        return {k: clean_nested_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nested_dict(v) for v in obj]
    elif pd.isna(obj):
        return None
    else:
        return obj

def default_converter(o):
    """Handles non-serializable objects for JSON serialization."""
    if pd.isna(o):
        return None
    raise TypeError(f"Object {o} is not serializable")

def format_created_range(year):
    """Creates a date range string for the document's creation time."""
    start_date = f"{year}-01-01"
    end_year = int(year) + 100
    end_date = f"{end_year}-01-01"
    return f"{start_date}, {end_date}"

def convert_txt_and_metadata(metadata_path, txt_folder_path, output_path):
    metadata_df = pd.read_csv(metadata_path)
    metadata_df.replace("NaN", None, inplace=True)

    with gzip.open(output_path, 'wt', encoding='utf-8') as gz_file:
        for _, row in tqdm(metadata_df.iterrows(), total=metadata_df.shape[0], desc="Processing records"):
            if pd.notna(row.get('filename')):
                filename = row['filename'].replace('.pdf', '') + '.txt'
                text_path = os.path.join(txt_folder_path, filename)
                
                if os.path.exists(text_path):
                    with open(text_path, 'r', encoding='utf-8') as txt_file:
                        text = txt_file.read()
                    # Be careful with NaN in source!
                    if pd.isna(row['source']):
                        source_value = "Unknown" # Note that Dolma don't accept None
                    else:
                        source_value = row['source']
                    
                    file_id = str(row.get('file_id')) if pd.notna(row.get('file_id')) else str(uuid.uuid4())
                    metadata = {key: value for key, value in row.to_dict().items() if key not in ['file_id', 'source']}
                    metadata["sub-source"] = source_value # Moving original source to metadata
                    document = {
                        "id": file_id,
                        "text": text,
                        "source": "memo", # Fixed source value
                        "added": datetime.datetime.now().strftime('%Y-%m-%d'),
                        "created": format_created_range(row.get('year', '1870')),
                        "metadata": clean_nested_dict(metadata)
                    }
                    
                    gz_file.write(json.dumps(document, default=default_converter))
                    gz_file.write("\n")
                else:
                    print(f"File not found: {text_path}")
            else:
                print("Filename missing in metadata")

    print("Dataset processing completed.")


def main():
    metadata_path =  '/work/github/Corpus-v1.1/MeMo-corpus-metadata-v1.1-2023-06-20.csv'
    txt_folder_path = '/work/github/Corpus-v1.1/normalized'
    output_path = '/work/dfm-data/pre-training/memo/documents/memo.jsonl.gz'
    convert_txt_and_metadata(metadata_path, txt_folder_path, output_path)

if __name__ == "__main__":
    main()
