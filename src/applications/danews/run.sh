# Logs of what have been run an in what order

echo "Apply quality filter to Articles"
python src/applications/danews/quality_filter.py

echo "Deduplicate articles"
python src/applications/danews/dedupe.py

echo "add metadata and generate datasheet"
python src/applications/danews/add_metadata.py
