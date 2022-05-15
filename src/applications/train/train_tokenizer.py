"""
Trains the tokenizer on the DFM corpus
"""
from wasabi import msg
from datasets import interleave_datasets

from dfm.data import load_dfm_dataset
from dfm.dfm_tokenizers import train_tokenizer, TokenizerConfig
from dfm.data.load_datasets import load_danews, load_dagw_dfm, load_hopetwitter, load_nat

columns_to_keep = ["text", "source"]
danews = load_danews(columns_to_keep=columns_to_keep)["train"]
dagw_dfm = load_dagw_dfm(columns_to_keep=columns_to_keep)["train"]
hopetwitter = load_hopetwitter(columns_to_keep = columns_to_keep)["train"]
nat = load_nat(columns_to_keep=columns_to_keep)["train"]
dataset = interleave_datasets([danews, dagw_dfm, hopetwitter, nat], probabilities=[0.10, 0.20, 0.20, 0.50])

msg.info("Started unigram training tokenizer")
t_config = TokenizerConfig(
    tokenizer_type = "unigram",
    vocab_size = 128000,
    lower_case = False,
    sentence_piece = True,
    add_prefix_space = True,
    byte_level = False)
tokenizer = train_tokenizer(
    corpus = dataset.take(5_000_000), 
    config=t_config,
    save_tokenizer=True,
    output_dir="ucloud-setup/dfm_tokenizer/unigram_5000000_docs_128000_tokens"
)   
msg.good("Finished unigram training tokenizer")
