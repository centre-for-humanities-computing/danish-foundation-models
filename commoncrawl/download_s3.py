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
import aioboto3
from botocore.config import Config

boto_config = Config(
   retries = {
      'max_attempts': 10,
      'mode': 'standard'
   }
)


parser = argparse.ArgumentParser()
parser.add_argument("--out_root", type=str, default="/mnt/usb/Common_Crawl_DK")
args = parser.parse_args()

files = glob.glob(
    f"/mnt/usb/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-50/subset=warc/*.parquet",
    recursive=True,
)
#crawl50 = duckdb.read_parquet(files, hive_partitioning=True)
files = glob.glob(
    f"/mnt/usb/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-40/subset=warc/*.parquet",
    recursive=True,
)
#crawl40 = duckdb.read_parquet(files, hive_partitioning=True)

query = """
WITH combined_crawls AS (
    SELECT * FROM read_parquet('/mnt/usb/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-50/subset=warc/*.parquet', hive_partitioning=True)
    UNION ALL
    SELECT * FROM read_parquet('/mnt/usb/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-40/subset=warc/*.parquet', hive_partitioning=True)
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

failed = False # flag to indicate to stop because downloads are failing
async def fetch_and_save(client, row):
    global failed
    path = make_path(row)
    if path in existing_files and os.path.getsize(path) == row["warc_record_length"]:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True) # ensure directory exists
    response = await client.get_object(Bucket='commoncrawl', Key=row['warc_filename'], Range=f'bytes={row["warc_record_offset"]}-{row["warc_record_offset"] + row["warc_record_length"] - 1}')
    meta = response['ResponseMetadata']
    if meta['HTTPStatusCode'] != 206:
        print(f"Failed to download {path}: HTTP {meta['HTTPStatusCode']}")
        failed = True
        return
    assert meta['HTTPHeaders']['content-length'] == str(row["warc_record_length"])
    async with aiofiles.open(path, 'wb') as f:
        await f.write(await response['Body'].read())
    if os.path.getsize(path) != row["warc_record_length"]:
        print(f"Failed to save {path}, size mismatch")
        failed = True
        os.remove(path)
        return

async def main():
    session = aioboto3.Session()
    async with session.client('s3', config=boto_config) as client:
        pbar = tqdm(total=num_rows)
        while batch := result.fetchmany(1000): # process in batches for the sake of memory
            if failed:
                exit(1)
            await asyncio.gather(*[fetch_and_save(client, row[0]) for row in batch])
            pbar.update(len(batch))
        pbar.close()

asyncio.run(main())

