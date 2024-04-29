#!/usr/bin/env bash
# Download the Columnar Index for the Common Crawl WARC files
CRAWL=CC-MAIN-2022-27
wget https://data.commoncrawl.org/crawl-data/$CRAWL/cc-index-table.paths.gz -O cc-index-table.paths.gz
gzip -d cc-index-table.paths.gz
grep 'subset=warc' cc-index-table.paths | wget -c -x -i - --base https://data.commoncrawl.org/