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

len(list(dataset.take(30)))
colnames = next(iter(danews)).keys()


dataset.remove_columns('timestamp')

t_config = TokenizerConfig(
    tokenizer_type = "unigram",
    vocab_size = 55000,
    lower_case = False,
    sentence_piece = True,
    add_prefix_space = True,
    byte_level = False)

msg.info("Started training tokenizer")

train_tokenizer(corpus = ds, config=t_config, save_tokenizer=True, output_dir="ucloud-setup/dfm_tokenizer")
msg.good("Finished training tokenizer")