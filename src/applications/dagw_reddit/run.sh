# Logs of what have been run an in what order

echo "Preprocessing (quality filter and deduplication) DAGW and Reddit"
python src/applications/dagw_reddit/proprocess.py

echo "Apply filter"
python src/applications/dagw_reddit/apply_filter.py

