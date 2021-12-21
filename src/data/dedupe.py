from typing import Dict

from text_dedup import MinHashDeduper

def min_hash_deduper(examples: Dict[str, list], text_column = "text", threshold=0.9, n_gram_size=5):
    """created a new feature "is_min_hash_duplicate" which indicate on the whether
    the example is a duplicate. Intended for batched inputs

    Args:
        threshold (float, optional): Threshold for what is a duplicate. Defaults to 0.9. 
        Values between 0.8 to 0.9 is probably reasonable.
        n_gram_size (int, optional): [description]. Defaults to 5.
    """
    deduper = MinHashDeduper(ngram_size=n_gram_size, threshold=threshold)
    groups = deduper.fit_transform(examples[text_column])
    groups_ = set()
    examples["is_min_hash_duplicate"] = []
    for group in groups:
        if group in groups_:
            examples["is_min_hash_duplicate"].append(True)
            continue
        examples["is_min_hash_duplicate"].append(False)
        groups_.add(group)
    return examples

def duplicate_filter(examples: Dict[str, list], dupe_indicator_columns = "is_min_hash_duplicate"):
    """duplicate filter for streaming datasets
    """
    return [e for e in examples in e[dupe_indicator_columns] is False]
