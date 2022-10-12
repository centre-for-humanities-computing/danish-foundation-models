"""
Trains the tokenizer on the DCC
"""
from pathlib import Path

from dfm.data import load_dcc
from dfm.dfm_tokenizers import TokenizerConfig, train_tokenizer

dataset = load_dcc(
    version="1.1.0",
    probabilities={"danews": 0.15, "dagw_dfm": 0.25, "hopetwitter": 0.25, "nat": 0.35},
)
train = dataset["train"]

vocab_sizes = [32_000, 50_000, 128_000]
n_docs = 100_000
save_path = Path("/data-big-projects/danish-foundation-models/tokenizers")

texts = [d["text"] for d in train.take(n_docs)]
print(f"Loaded {n_docs} documents")

# for vocab_size in vocab_sizes:
vocab_size = 32_000
t_config = TokenizerConfig(
    tokenizer_type="unigram",
    vocab_size=vocab_size,
    lower_case=False,
    sentence_piece=True,
    add_prefix_space=True,
    byte_level=False,
)
tokenizer = train_tokenizer(
    corpus=texts,
    config=t_config,
    save_tokenizer=True,
    output_dir=save_path / f"unigram_{n_docs}_docs_{vocab_size}_vocab",
)
