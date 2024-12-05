# European Union Publications Office - Cellar

The data is pulled in two steps:
1. `catalog.py` - Pull a list of all publictaions from `start_date` to `end_date`
2. `ingest.py` - Download the individual publications and process them.