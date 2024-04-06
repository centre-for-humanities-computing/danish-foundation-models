import duckdb
import glob
import httpx
from pathlib import Path
import argparse
import asyncio
import aiofiles
from tqdm import tqdm
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--out_root", type=str, default="/mnt/Common_Crawl/")
args = parser.parse_args()

files = glob.glob(
    f"/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-50/subset=warc/*.parquet",
    recursive=True,
)
crawl50 = duckdb.read_parquet(files, hive_partitioning=True)
files = glob.glob(
    f"/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-40/subset=warc/*.parquet",
    recursive=True,
)
crawl40 = duckdb.read_parquet(files, hive_partitioning=True)

query = """
WITH combined_crawls AS (
    SELECT * FROM read_parquet('/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-50/subset=warc/*.parquet', hive_partitioning=True)
    UNION ALL
    SELECT * FROM read_parquet('/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-40/subset=warc/*.parquet', hive_partitioning=True)
)
SELECT STRUCT_PACK(url, 
       warc_filename,
       warc_record_offset,
       warc_record_length,
       warc_segment) AS crawl_data
FROM combined_crawls
WHERE subset = 'warc'
  AND url_host_tld = 'dk'
""" 

result = duckdb.sql(query)
num_rows = result.shape[0]

# get all existing files at once, for fast resumption
existing_files = set(os.path.join(dirpath,f) for (dirpath, dirnames, filenames) in os.walk(args.out_root) for f in filenames)

def make_path(row):
    return os.path.join(args.out_root, f"{row['warc_filename']}-bytes={row['warc_record_offset']}-{row['warc_record_offset'] + row['warc_record_length'] - 1}")

async def fetch_and_save(client, row):
    path = make_path(row)
    if path in existing_files:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True) # ensure directory exists
    headers = {
        'Range': f'bytes={row["warc_record_offset"]}-{row["warc_record_offset"] + row["warc_record_length"] - 1}'
    }
    async with client.stream("GET", f"https://data.commoncrawl.org/{row['warc_filename']}", headers=headers, timeout=None) as response:
        async with aiofiles.open(path, 'wb') as f:
            async for chunk in response.aiter_bytes():
                await f.write(chunk)

async def main():
    async with httpx.AsyncClient(http2=True, limits=httpx.Limits(max_connections=100)) as client:
        pbar = tqdm(total=num_rows)
        while batch := result.fetchmany(1000): # process in batches for the sake of memory
            await asyncio.gather(*[fetch_and_save(client, row[0]) for row in batch])
            pbar.update(len(batch))
        pbar.close()

asyncio.run(main())

