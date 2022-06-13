import os
import time
from typing import List

import spacy
from datasets import load_dataset
from dfm.description.description_patterns import (
    danish_adult_words,
    get_female_gendered_patterns,
    get_gender_name_patterns,
    get_male_gendered_patterns,
    get_muslim_name_patterns,
    get_negative_word_patterns,
    get_occupation_patterns,
    get_positive_word_patterns,
    get_religion_patterns,
)
from dfm.description.match_counter import MatchCounter


def create_patterns() -> List:
    """Generates the patterns we've selected for the present analyses.

    Returns:
        List: List of spacy pattern containers.
    """
    any_token_pattern = [{"tokens": [{"TEXT": {"REGEX": ".+"}}]}]

    gender_pronoun_patterns = [
        {"gender_male_pronoun": [{"LOWER": "han"}]},
        {"gender_female_pronoun": [{"LOWER": "hun"}]},
    ]

    # Adult words
    adult_patterns = MatchCounter.term_list_to_spacy_match_patterns(
        danish_adult_words, label_prefix="porn_"
    )

    return (
        any_token_pattern
        + gender_pronoun_patterns
        + get_religion_patterns()
        + get_occupation_patterns()
        + get_muslim_name_patterns()
        + get_gender_name_patterns()
        + get_male_gendered_patterns()
        + get_female_gendered_patterns()
        + get_positive_word_patterns()
        + get_negative_word_patterns()
        + adult_patterns
    )


if __name__ == "__main__":
    from pathlib import Path

    all_patterns = create_patterns()

    ds = load_dataset("DDSC/partial-danish-gigaword-no-twitter")
    ds_sharded = ds.shuffle()["train"].shard(
        num_shards=10000, index=0
    )  # Work on 1/100th of DGW

    nlp = spacy.blank("da")
    nlp.max_length = 50000000

    MatchCounter = MatchCounter(match_patterns=all_patterns, nlp=nlp)

    start_time = time.time()

    dgw_processed = ds_sharded.map(
        lambda batch: MatchCounter.count(batch["text"]),
        batched=True,
        batch_size=50,
        num_proc=16,
    )

    print(f"\n\n--- Execution time was {time.time() - start_time} seconds ---")

    save_path = os.path.join("csv")
    save_path = Path(save_path)  # format as path
    save_path.mkdir(parents=False, exist_ok=True)  # only create if needed

    dgw_processed = dgw_processed.remove_columns(
        ["text", "doc_id", "LICENSE", "uri", "date_built"]
    )  # Remove irrelevant columns

    dgw_processed.to_csv("csv/output_100.csv")
