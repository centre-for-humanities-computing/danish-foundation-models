from datasets import DatasetDict, load_dataset, Dataset
import pandas as pd
from sklearn.model_selection import train_test_split

def load_dagw(path):
    ds = load_dataset("json", path)
    return ds

def make_train_val_test(ds: Dataset, train_prop: float, )


if __name__ == "__main__":

    CLEANED_DAGW_PATH = "/work/data/dagw-cleaned/dagw_clean.jsonl"

    ds = load_dagw(CLEANED_DAGW_PATH)

    ds = ds.filter(lambda example: example["passed_quality_filter"] is True)

    source = ds["source"]
    df = pd.DataFrame(source, columns=["source"])
    df = df.reset_index()

    # 70/15/15 split
    train, tmp = train_test_split(df, test_size=0.3, stratify="source")
    val, test = train_test_split(tmp, test_size=0.5, stratify="source")

    train_idx = train["index"]
    val_idx = train["index"]
    test_idx = train["index"]

    train = ds.select(train_idx)
    val = ds.select(val_idx)
    test = ds.select(test_idx)
    
    ds = DatasetDict(
    {
        "train": train_test["train"],
        "test": test_valid["test"],
        "val": test_valid["train"],
    }
    )