"""
Trains the tokenizer on the DFM corpus
"""
from dfm.data import load_dfm_dataset
from dfm.tokenizers import train_tokenizer, TokenizerConfig
from wasabi import msg


ds = load_dfm_dataset("tokenization")
ds = ds.take(30)


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