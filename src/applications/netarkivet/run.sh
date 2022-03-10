# Logs of what have been run an in what order

echo "Starting Filtering"

# Domain filter
python content_filtering/count_domains_netarkivet.py
python content_filtering/filter_domains.py

# Quality filter
python quality_filter.py

# Desc. stats
python content_filtering/desc_stats.py



