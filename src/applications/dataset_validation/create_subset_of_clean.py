from datetime import date
from typing import Iterable, Optional

from dfm.dataset_validation.rating_interface import ExampleRater
from dfm.cleaning import SentenceFilter, QualityFilter

import ndjson


def text_generator(seed, max_texts=5000):
    from dfm.data.load_datasets import load_nat

    datasets = load_nat(seed=seed)["train"]
    texts = (text["text"].replace("\xa0", "\n") for text in iter(datasets))
    if max_texts:
        texts = [next(texts) for i in range(max_texts)]

    texts = post_clean(texts)
    return texts

def post_clean(texts: Iterable[str]) -> Iterable[str]:
    global n_text_cleaned
    def __text_genw_counter(texts):
        for t in texts:
            n_text_cleaned += 1
            yield texts
    sf = SentenceFilter(
        filter_names = None,
        title_cased_words_threshold = 0.7,
        min_num_words = 3,
        curly_brackets_threshold = 2,
    )
    qf = QualityFilter(
        min_stop_words = 2,
        mean_word_length  = (3, 10),
        doc_length = (50, 100_000),
        alpha_ratio= 0.8,
        symbol_2_word_hashtag= 0.1,
        symbol_2_word_ellipsis = 0.1,
        max_p_begin_bullets = 0.9,
        max_p_end_ellipsis = 0.3,
        min_bullets = 2,
        min_ellipsis = 2,
        duplicate_lines_chr_fraction = 0.2,
        duplicate_paragraph_chr_fraction = 0.2,
        top_ngram_chr_fraction_thresholds = [0.20, 0.18, 0.16],
        top_ngram_chr_fraction_range = (2, 4),
        top_ngram_min_count = 3,
        duplicate_n_gram_fraction_thresholds = [
            0.15,
            0.14,
            0.13,
            0.12,
            0.11,
            0.10,
        ],
        duplicate_n_gram_fraction_range = (5, 10),
        max_length= 5_000_000,
        string_filter = None,
        ignore_filters = [],
        language_detection_tool = "langdetect",
        language_threshold = 0.90,
        languages = ["da"],
        short_long_sentence_length_split = 30,
        short_long_sentence_threshold  = 0.5,
    )
    texts = sf(texts)
    texts = qf(texts)
    return texts


if __name__ == "__main__":
    texts = text_generator(seed=2)
    texts = [t.text for t in texts]
    # Fix: max length on texts segments
    texts_ = [{"text": t} for t in texts]
    with open('/work/netarkivet-cleaned/temp/tagging_texts.ndjson', 'w') as f:
        ndjson.dump(texts_, f)
    