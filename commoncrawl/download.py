import duckdb, glob


crawl50 = "CC-MAIN-2023-50",
files = glob.glob(
    f"/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl={crawl50}/subset=warc/*.parquet",
    recursive=True,
)
crawl50 = duckdb.read_parquet(files, hive_partitioning=True)
crawl40 = "CC-MAIN-2023-50",
files = glob.glob(
    f"/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl={crawl40}/subset=warc/*.parquet",
    recursive=True,
)
crawl40 = duckdb.read_parquet(files, hive_partitioning=True)

query = """
SELECT url_host_registered_domain, 
       COUNT(*) AS num_pages,
       SUM(warc_record_length) AS total_bytes,
       (SUM(CASE WHEN content_languages LIKE '%dan%' THEN 1 ELSE 0 END) * 100.0) / COUNT(*) AS danish_pages_percentage
FROM (
    SELECT * FROM crawl50
    UNION
    SELECT * FROM crawl40
) AS combined_crawls
WHERE subset = 'warc'
  AND url_host_tld = 'dk'
GROUP BY url_host_registered_domain
ORDER BY total_bytes DESC
"""

result = duckdb.sql(query)
print(result)

# duckdb.sql(f'''COPY result TO '{crawl}.csv' (HEADER, DELIMITER ',')''')
