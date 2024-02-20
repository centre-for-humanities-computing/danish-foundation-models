import duckdb, glob

crawl = "CC-MAIN-2023-40"
files = glob.glob(f'/mnt/Common_Crawl/data.commoncrawl.org/cc-index/**/crawl={crawl}/subset=warc/*.parquet', recursive=True)
ccindex = duckdb.read_parquet(files, hive_partitioning=True)
# Columns:
# url_surtkey: Canonical form of URL with host name reversed
# url: URL that was archived
# url_host_name: The host name
# url_host_tld: The TLD (e.g. au)
# url_host_2nd_last_part, … url_host_5th_last_part: The parts of the host name separated by .
# url_host_registry_suffix: e.g. .com.au
# url_host_private_domain
# url_protocol: e.g. https
# url_port: The port accesed, it seems to be blank for default ports (80 for http, 443 for https).
# url_path: The path of the URL (everything from the first / to the query parameter starting at ?)
# url_query: Query parameter; everything after the ?
# fetch_time: When the page was retrieved
# fetch_status: The HTTP status of the request (e.g. 200 is OK)
# content_digest: A digest to uniquely identify the content
# content_mime_type: The type of content in the header
# content_mime_detected: The type of content detected
# content_charset: The characterset of the data (e.g. UTF-8)
# content_languages: Languages declared of the content
# warc_filename: The filename the archived data is in
# warc_record_offset: The offset in bytes in the archived file where the corresponding data starts
# warc_record_length: The length of the archived data in bytes
# warc_segment: The segment the data is archived in; this is part of the filename
# crawl: The id of the crawl (e.g. CC-MAIN-YYYY-WW where YYYY is the year and WW is the ISO week of the year).
# subset: Is this the ‘warc’, or ‘robotstxt’, or ‘crawldiagnostics’

query = """
SELECT url_host_registered_domain, 
       COUNT(*) AS num_pages,
       SUM(warc_record_length) AS total_bytes,
       (SUM(CASE WHEN content_languages LIKE '%dan%' THEN 1 ELSE 0 END) * 100.0) / COUNT(*) AS danish_pages_percentage
FROM ccindex
WHERE subset = 'warc'
  AND url_host_tld = 'dk'
GROUP BY url_host_registered_domain
ORDER BY total_bytes DESC
"""

result = duckdb.sql(query)

duckdb.sql(f'''COPY result TO '{crawl}.csv' (HEADER, DELIMITER ',')''')



