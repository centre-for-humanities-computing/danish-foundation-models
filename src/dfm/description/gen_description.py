import os
import sys
import time
from datasets import load_dataset


import spacy

sys.path.append(".")

from dfm.description.description_patterns import (
    female_gendered_terms,
    male_gendered_terms,
    occupation_pattern_list,
    danish_adult_words,
    get_muslim_name_patterns,
    get_gender_name_patterns,
)

from dfm.description.matchcounter import MatchCounter


def remove_irrelevant_columns(ds):
    return ds.remove_columns(["text", "doc_id", "LICENSE", "uri", "date_built"])


def create_patterns():
    any_token_pattern = [{"tokens": [{"TEXT": {"REGEX": ".+"}}]}]

    # Religion
    religion_patterns = [
        {"atheist": [{"LOWER": {"REGEX": "ath{0,1}eis.*"}}]},
        {"buddhist": [{"LOWER": {"REGEX": "buddh{0,1}.*"}}]},
        {"christian": [{"LOWER": {"REGEX": "kriste.*"}}]},
        {"hindu": [{"LOWER": {"REGEX": "hindu.*"}}]},
        {"muslim": [{"LOWER": {"REGEX": "muslim.*"}}]},
        {"jew": [{"LOWER": {"REGEX": "jødi.*"}}]},
        {"jew": [{"LOWER": {"REGEX": "(?!jødeskæg)jøde.*"}}]},  # Jødeskæg == Stueplante
    ]

    muslim_name_patterns = get_muslim_name_patterns()

    # Genders
    gender_name_patterns = get_gender_name_patterns()

    gender_pronoun_patterns = [
        {"male_pronoun": [{"LOWER": "han"}]},
        {"female_pronoun": [{"LOWER": "hun"}]},
    ]

    # Gendered terms
    # List is a partial translation of Rae et al. 2022, p. 95
    male_gendered_term_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        male_gendered_terms, label="male_gendered_terms"
    )
    female_gendered_term_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        female_gendered_terms, label="female_gendered_terms"
    )

    # Occupations
    # List is a partial translation of Rae et al. 2022, p. 95
    occupation_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        occupation_pattern_list, label_prefix="occu_"
    )

    # Adult words
    adult_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        danish_adult_words, label_prefix="porn_"
    )

    return (
        any_token_pattern
        + religion_patterns
        + muslim_name_patterns
        + gender_name_patterns
        + gender_pronoun_patterns
        + male_gendered_term_patterns
        + female_gendered_term_patterns
        + occupation_patterns
        + adult_patterns
    )


if __name__ == "__main__":
    all_patterns = create_patterns()

    ds = load_dataset("DDSC/partial-danish-gigaword-no-twitter")
    ds_sharded = ds.shuffle()["train"].shard(
        num_shards=100, index=0
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

    from pathlib import Path

    save_path = os.path.join("csv")
    save_path = Path(save_path)  # format as path
    save_path.mkdir(parents=False, exist_ok=True)  # only create if needed

    remove_irrelevant_columns(dgw_processed).to_csv("csv/output_100.csv")
