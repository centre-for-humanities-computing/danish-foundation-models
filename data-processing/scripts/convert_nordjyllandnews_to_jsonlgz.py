'''
Huggingface Repo: https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization
{
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "foo",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp ai2 acquired this data
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available)
    "metadata": {...}        # OPTIONAL: source-specific metadata
}
'''

import pyarrow.parquet as pq # type: ignore
import gzip
from datetime import datetime, timedelta
import pandas as pd # type: ignore
import json

def format_created_range(created_date, delay_days=365):
    """Create a formatted string representing a time range starting from `publish_date`."""
    start_date = datetime.strptime(created_date, "%Y-%m-%dT%H:%M:%S.000Z")
    end_date = start_date + timedelta(days=delay_days)
    return f"{start_date.strftime('%Y-%m-%d')}, {end_date.strftime('%Y-%m-%d')}"

def parquet_to_jsonlgz(input_path, output_path):
    """Convert .parquet to newline-delimited json.gz."""
    pds = pd.read_parquet(input_path)
    with gzip.open(output_path, 'wt', encoding='utf-8') as out_file:
        for idx, row in pds.iterrows():
            transformed = {
                "id": f'nordjylland-news{idx}',
                "text": row.get("text", ""),
                "source": "nordjylland_news",
                "added": datetime.now().strftime('%Y-%m-%d'),
                "created": format_created_range(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')),
                "metadata": {
                    "summary": row.get("summary", ""),
                    "text_len": row.get("text_len", ""),
                    "summary_len": row.get("summary_len", "")
                    "sub-source": "TV2 Nord"
                }
            }
            json_str = json.dumps(transformed)
            out_file.write(json_str + '\n')

def main():
    parquet_path = "/work/github/nordjylland-news-summarization/data/train-00000-of-00001-4fb110c0f6314175.parquet"
    converted_path = "/work/dfm-data/pre-training/nordjylland_news/documents/nordjylland_news.jsonl.gz"

    parquet_to_jsonlgz(parquet_path, converted_path)

if __name__ == '__main__':
    main()