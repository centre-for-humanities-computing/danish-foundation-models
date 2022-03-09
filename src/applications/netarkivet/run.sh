# runs the preprocessing of netarkivet.

echo "Starting script"
python content_filtering/count_domains_netarkivet.py
python content_filtering/filter_domains.py

python content_filtering/desc_stats.py

