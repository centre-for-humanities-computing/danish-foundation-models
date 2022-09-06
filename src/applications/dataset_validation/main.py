from datetime import date
from typing import Iterable, Optional

from dfm.cleaning import QualityFilter, SentenceFilter
from dfm.dataset_validation.rating_interface import ExampleRater

n_text_cleaned = 0
n_char_total = 0


def text_generator(seed, n_texts: Optional[int], max_texts: Optional[int]):
    from dfm.data.load_datasets import load_nat

    datasets = load_nat(seed=seed)["train"]
    texts = (text["text"].replace("\xa0", "\n") for text in iter(datasets))

    if max_texts:
        texts = [next(texts) for i in range(max_texts)]
    texts = post_clean(texts)
    for i, text in enumerate(texts):
        if n_texts and i > n_texts:
            break
        for newline in text.split("\n"):
            if newline:
                yield newline


def post_clean(texts: Iterable[str]) -> Iterable[str]:
    def __text_genw_counter(texts):
        global n_text_cleaned
        global n_char_total
        for t in texts:
            n_text_cleaned += 1
            n_char_total += len(t)
            yield t

    sf = SentenceFilter(
        filter_names=None,
        title_cased_words_threshold=0.7,
        min_num_words=3,
        curly_brackets_threshold=2,
    )
    qf = QualityFilter(
        min_stop_words=2,
        mean_word_length=(3, 10),
        doc_length=(50, 100_000),
        alpha_ratio=0.8,
        symbol_2_word_hashtag=0.1,
        symbol_2_word_ellipsis=0.1,
        max_p_begin_bullets=0.9,
        max_p_end_ellipsis=0.3,
        min_bullets=2,
        min_ellipsis=2,
        duplicate_lines_chr_fraction=0.2,
        duplicate_paragraph_chr_fraction=0.2,
        top_ngram_chr_fraction_thresholds=[0.20, 0.18, 0.16],
        top_ngram_chr_fraction_range=(2, 4),
        top_ngram_min_count=3,
        duplicate_n_gram_fraction_thresholds=[
            0.15,
            0.14,
            0.13,
            0.12,
            0.11,
            0.10,
        ],
        duplicate_n_gram_fraction_range=(5, 10),
        max_length=5_000_000,
        string_filter=None,
        language_detection_tool="langdetect",
        language_threshold=0.90,
        languages=["da"],
        short_long_sentence_length_split=30,
        short_long_sentence_threshold=0.5,
    )
    texts = sf(__text_genw_counter(texts))
    texts = qf(texts)
    texts = (t.text for t in texts)
    return texts


if __name__ == "__main__":
    MY_NAME = "kenneth"
    SESSION = "session_1"
    N_TO_RATE = 100.0  # n text documents to rate (!= sentences)
    max_texts = 1000
    seed = 2  # seeds already used: 2,
    max_len = 2000

    gen = text_generator(seed=seed, n_texts=N_TO_RATE, max_texts=max_texts)
    texts = list(gen)
    print(f"N texts to obtain {N_TO_RATE}: {n_text_cleaned}")
    print(f"n_char_cleaned/n_char_total = {sum(len(t) for t in texts) /n_char_total }")
    # Fix: max length on texts segments
    text_splits = [
        text[i : i + max_len] for text in texts for i in range(0, len(text), max_len)
    ]

    rater = ExampleRater(
        examples=text_splits,
        output_path=f"/work/netarkivet-cleaned/tagging/{MY_NAME}_{SESSION}_{date.today()}.csv",
    )

    rater.rate_examples()

    # proportion af "»"
    # ratio af {...}
    # Siden blev behandlet på {0.164} sekund"
