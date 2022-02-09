"""
Extract description of using the quality filter on DAGW

To run profile the code:

.. code::
    pip install snakeviz

    # run script with cProfile
    python -m cProfile -o tmp.prof src/dagw_clean.py

    # view result
    snakeviz tmp.prof
"""

import sys
import ndjson
import time

sys.path.append("..")
sys.path.append(".")


from dfm.cleaning import QualityFilter
from dfm.data.load import load_dfm_dataset


s = time.time()

ds = load_dfm_dataset("dagw", streaming=False)

ds = ds.remove_columns(["LICENSE"])

batch_size = 1024 * 4


def q_filter(batch, batch_size=batch_size):
    qf = QualityFilter()
    batch["filtered"] = list(qf.describe_filter(batch["text"], batch_size=batch_size))
    return batch


ds = ds.map(q_filter, batched=True, batch_size=batch_size, num_proc=12)

ds = ds.remove_columns(["text"])

with open("DAGW_filter.ndjson", "w") as f:
    writer = ndjson.writer(f, ensure_ascii=False)

    for sample in ds:
        writer.writerow(sample)

print("Done, took:", time.time() - s)
