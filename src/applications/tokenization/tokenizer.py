from typing import List, Set

from compound_words import sammensatte_ord

from transformers import AutoTokenizer


def cumlength(array):
    cum_len = []
    cum_sum = 0
    for var in array:
        cum_sum += len(var)
        cum_len.append(cum_sum)
    return cum_len


def calc_metrics(split, gold_split):
    split = set(split)
    gold_split = set(gold_split)

    true_positives = split.intersection(gold_split)
    false_positives = {s for s in split if s not in true_positives}
    false_negative = {s for s in gold_split if s not in true_positives}
    TP = len(true_positives)
    FP = len(false_positives)
    FN = len(false_negative)

    return {
        "true_positives": TP,
        "false_positives": FP,
        "false_negatives": FN,
        "is_correct": len(true_positives) == len(gold_splits),
    }


words, compounds = zip(*sammensatte_ord.items())
# unnest
compounds = [[c for subcomp in compound for c in subcomp] for compound in compounds]
gold_splits = [set(cumlength(comp[:-1])) for comp in compounds]


def validate_tokenizer(
    tokenizer: AutoTokenizer, gold_splits: List[Set[int]], words: List[str]
) -> dict:
    # if sentencepiece tokenizer:
    if "sp_model_kwargs" in tokenizer.init_kwargs:
        tokenized = [tokenizer.tokenize(word) for word in words]
        word_splits = [
            cumlength([subtoken.replace("▁", "") for subtoken in word[:-1]])
            for word in tokenized
        ]
    else:
        encoding = tokenizer(list(words), add_special_tokens=False)
        tokenized = [encoding[i].tokens for i, word in enumerate(words)]
        # extract index of splits for each token
        word_splits = [
            [i[0] for i in encoding[word_idx].offsets[1:]]
            for word_idx, _ in enumerate(words)
        ]

    perf_metrics = [
        calc_metrics(split, gold_split)
        for split, gold_split in zip(word_splits, gold_splits)
    ]

    perf_scores = {
        k: sum([p[k] for p in perf_metrics])
        for k in ["true_positives", "false_positives", "false_negatives"]
    }
    precision = perf_scores["true_positives"] / (
        perf_scores["true_positives"] + perf_scores["false_positives"]
    )
    recall = perf_scores["true_positives"] / (
        perf_scores["true_positives"] + perf_scores["false_negatives"]
    )
    f1 = 2 * precision * recall / (precision + recall)
    f2 = (1 + 2**2) * precision * recall / (2**2 * precision + recall)
    jaccard_index = perf_scores["true_positives"] / (
        perf_scores["true_positives"]
        + perf_scores["false_positives"]
        + perf_scores["false_negatives"]
    )

    result = {
        "precision": precision,
        "recall": recall,
        "f1-score": f1,
        "f2-score": f2,
        "jaccard-index": jaccard_index,
        "true_positives": perf_scores["true_positives"],
        "false_positives": perf_scores["false_positives"],
        "false_negatives": perf_scores["false_negatives"],
        "models_splits": word_splits,
        "gold_splits": gold_splits,
        "perfomance_metrics_pr_sample": perf_metrics,
        "model_tokenization": tokenized,
    }
    return result


tokenizer_names = [
    "Maltehb/danish-bert-botxo",
    "Maltehb/aelaectra-danish-electra-small-cased",
    "Maltehb/aelaectra-danish-electra-small-uncased",
    "bert-base-multilingual-uncased",
    "microsoft/mdeberta-v3-base",
]
result = []
for name in tokenizer_names:
    tokenizer = AutoTokenizer.from_pretrained(name)
    result_ = validate_tokenizer(tokenizer, gold_splits, words=words)
    result_["tokenizer"] = name
    result.append(result_)

# write to csv

from tokenizers import Tokenizer
from transformers import PreTrainedTokenizerFast

for i in [
    "UNIGRAM",
    "BPE",
    "WORDPIECE",
    "UNIGRAM_500000_docs",
    "UNIGRAM_128000_tokens",
    "UNIGRAM_32000_tokens",
]:
    tokenizer = Tokenizer.from_file(f"/Users/au561649/Downloads/tokenizer_{i}.json")
    tokenizer = PreTrainedTokenizerFast(tokenizer_object=tokenizer)
    result_ = validate_tokenizer(tokenizer, gold_splits, words=words)

    print(i)
    for k in [
        "precision",
        "recall",
        "f1-score",
        "f2-score",
        "jaccard-index",
    ]:
        print(f"\t{k}: {result_[k]:.2f}")


interfixes = zip(*[gold_splits[i] for i, (word, comp) in enumerate(sammensatte_ord.items()) if ["s"] in comp]
words, compounds = zip(*sammensatte_ord.items())
compounds = [[c for subcomp in compound for c in subcomp] for compound in compounds]
gold_splits = [set(cumlength(comp[:-1])) for comp in compounds]


interfix_word = [word for i, (word, comp) in enumerate(sammensatte_ord.items()) if ["s"] in comp]
interfix_word
for i in [
    "UNIGRAM",
    "BPE",
    "WORDPIECE",
    "UNIGRAM_500000_docs",
    "UNIGRAM_128000_tokens",
    "UNIGRAM_32000_tokens",
]:
    tokenizer = Tokenizer.from_file(f"/Users/au561649/Downloads/tokenizer_{i}.json")
    tokenizer = PreTrainedTokenizerFast(tokenizer_object=tokenizer)
    result_ = validate_tokenizer(tokenizer, interfix_gold, words=interfix_word)

    print(i)
    for k in [
        "precision",
        "recall",
        "f1-score",
        "f2-score",
        "jaccard-index",
    ]:
        print(f"\t{k}: {result_[k]:.2f}")
gold_splits

# good splits not accounted for
# word | gold splits | model splits | Correct split |
# aborttilhænger  |  ['abort', 'tilhænger']  |  ['abort', '##til', '##hænger']  |  [True, False]
# arbejdshandske  |  ['arbejd', 's', 'handske']  |  ['arbejds', '##hand', '##ske']  |  [True, False]
# badmintonketsjer  |  ['badminton', 'ketsjer']  |  ['badminton', '##kets', '##jer']  |  [True, False]
# bananplantage  |  ['banan', 'plantage']  |  ['banan', '##plant', '##age']  |  [True, False]
# bilfærge  |  ['bil', 'færge']  |  ['bil', '##fær', '##ge']  |  [True, False]

# bad splits (e.g. due to greedy splits)
# abekattestreg  |  ['abe', 'katte', 'streg']  |  ['abe', '##kat', '##test', '##reg']
# abortmodstander  |  ['abort', 'modstander']  |  ['abort', '##mods', '##ta', '##nd', '##er']  |  [True, False, False, False]
# absorptionslyddæmper  |  ['absorptions', 'lyd', 'dæmper']  |  ['absor', '##ption', '##sl', '##yd', '##dæmp', '##er']  |  [False, False, False, True, False]
# dødtræt  |  ['død', 'træt']  |  ['dødt', '##ræt']  |  [False]

# score = sum(Correct split)/len(Correct split)
