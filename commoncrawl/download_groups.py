import duckdb
import glob
import httpx
import argparse
import asyncio
import aiofiles
from tqdm import tqdm
import os

from retry_transport import RetryTransport

parser = argparse.ArgumentParser()
parser.add_argument("--out_root", type=str, default="/mnt/Common_Crawl/Common_Crawl_DK_cat")
args = parser.parse_args()

files = glob.glob(
    f"/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-50/subset=warc/*.parquet",
    recursive=True,
)
#crawl50 = duckdb.read_parquet(files, hive_partitioning=True)
files = glob.glob(
    f"/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-40/subset=warc/*.parquet",
    recursive=True,
)
#crawl40 = duckdb.read_parquet(files, hive_partitioning=True)

query = """
PRAGMA enable_progress_bar;
WITH combined_crawls AS (
    SELECT * FROM read_parquet('/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-50/subset=warc/*.parquet', hive_partitioning=True)
    WHERE subset = 'warc' AND url_host_tld = 'dk'
    UNION ALL
    SELECT * FROM read_parquet('/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl=CC-MAIN-2023-40/subset=warc/*.parquet', hive_partitioning=True)
    WHERE subset = 'warc' AND url_host_tld = 'dk'
)
SELECT warc_filename, LIST(warc_record_offset), LIST(warc_record_length)
FROM combined_crawls
GROUP BY warc_filename
"""

result = duckdb.sql(query)
num_rows = result.shape[0]

# get all existing files at once, for fast resumption
existing_files = set(os.path.join(dirpath,f) for (dirpath, dirnames, filenames) in os.walk(args.out_root) for f in filenames)

def make_path(warc_filename: str):
    return os.path.join(args.out_root, warc_filename)

failed = False # flag to indicate to stop because downloads are failing
async def fetch_and_save(client: httpx.AsyncClient, row: tuple[str, list[int], list[int]]):
    global failed

    warc_filename = row[0]
    warc_record_offset_list = row[1]
    warc_record_length_list = row[2]
    path = make_path(warc_filename)
    if (path in existing_files) and (os.path.getsize(path) == sum(warc_record_length_list)):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True) # ensure directory exists

    async with aiofiles.open(path, 'wb') as output_file:
        for warc_record_offset, warc_record_length in zip(warc_record_offset_list, warc_record_length_list):
            headers = {
                'Range': f'bytes={warc_record_offset}-{warc_record_offset + warc_record_length - 1}'
            }
            response = await client.get(f"https://data.commoncrawl.org/{warc_filename}", headers=headers, timeout=None)
            if response.status_code != 206:
                print(f"Failed to download {path}: HTTP {response.status_code}")
                failed = True
                break
            await output_file.write(response.content)
    if os.path.getsize(path) != sum(warc_record_length_list):
        print(f"Failed to save {path}, size mismatch")
        failed = True
        os.remove(path)
        return

async def main():
    async with httpx.AsyncClient(http2=False, limits=httpx.Limits(max_connections=1), transport=RetryTransport(wrapped_transport=httpx.AsyncHTTPTransport())) as client:
        pbar = tqdm(total=num_rows)
        while batch := result.fetchmany(20): # process in batches for the sake of memory
            if failed:
                exit(1)
            await asyncio.gather(*[fetch_and_save(client, row) for row in batch])
            pbar.update(len(batch))
        pbar.close()

asyncio.run(main())

