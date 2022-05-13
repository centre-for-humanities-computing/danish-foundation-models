from pathlib import Path
from datasets import load_from_disk

if __name__ == "__main__":
    path = Path("/work") / "dagw-clean" / "dagw_reddit_filtered_v1.0.0.arrow"

    ds = load_from_disk(path)

    ds.push_to_hub("DDSC/dagw_reddit_filtered_v1.0.0", private=True)