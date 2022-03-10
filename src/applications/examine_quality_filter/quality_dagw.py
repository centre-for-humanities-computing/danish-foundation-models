"""
Extract description of using the quality filter on DAGW

To run profile the code:

.. code::
    pip install snakeviz

    # run script with cProfile
    python -m cProfile -o tmp.prof src/applications/examine_quality_filter/quality_dagw.py 

    # view result
    snakeviz tmp.prof
"""

import sys
import ndjson
import time

sys.path.append("..")
sys.path.append(".")


from src.dfm.cleaning import QualityFilter
from src.dfm.data.load import load_dfm_dataset


def q_filter(batch):
    qf = QualityFilter()
    batch["filtered"] = list(qf.describe_filter(batch["text"], batch_size=1024))
    return batch


s = time.time()
ds = load_dfm_dataset("dagw", streaming=False)
ds = ds.remove_columns(["LICENSE"])

ds = ds.shard(num_shards=200, index=1)
ds = ds.map(
    q_filter, batched=True, batch_size=1024, num_proc=1, load_from_cache_file=False
)
print("Done, took:", time.time() - s)

with open("DAGW_filter.ndjson", "w") as f:
    writer = ndjson.writer(f, ensure_ascii=False)
    for sample in ds:
        writer.writerow(sample)
