# What have been run and in what order.

echo "Starting Filtering"

# Domain filter
python3 content_filtering/count_domains_netarkivet.py
python3 content_filtering/filter_domains.py

echo "Apply quality filter"
python3 quality_filter.py

echo "Start deduplication"
python3 dedupe.py

echo "Create descriptive stats"

python3 desc_stats.py
python3 create_metadata_csv.py
python3 extract_summary_statistics.py

# update dataset with metadata column
python3 add_is_duplicate_column.py

echo "Apply filters"
python3 apply_filters.py


