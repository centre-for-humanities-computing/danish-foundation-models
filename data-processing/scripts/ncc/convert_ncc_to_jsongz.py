# """
# Download  The Norwegian Colossal Corpus, convert to jsonl.gz with each document following the format:

# {
#     "id": "...",             # MANDATORY: source-specific identifier
#     "text": "foo",           # MANDATORY: textual content of the document
#     "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
#     "added": "...",          # OPTIONAL: timestamp ai2 acquired this data
#     "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available)
#     "metadata": {...}        # OPTIONAL: source-specific metadata
# }
# """

# import datasets


# ncc_full = datasets.load_dataset("NbAiLab/NCC", streaming=True, split="train")
# ds = ncc_full.take(1000)

# # %%
# sample = list(ds.take(10))

# # %%
# # dolma format for a single observation
# obs = sample[0]

# new_obj = {
#     "id": obs["id"],
#     "text": obs["text"],
#     "source": "NCC",
#     "added": "2024-03-01T00:00:00.000Z",
#     "created": f"{obs["publish_year"]}-01-01T00:00:00.000Z",
#     "metadata": {
#         "doc_type": obs["doc_type"],
#         "lang_fasttext": obs["lang_fasttext"],
#         "lang_fasttext_conf": obs["lang_fasttext_conf"],
#     }
# } 


# ds.to_json("data.jsonl.gz", orient="records", lines=True, compression="gzip")  # type: ignore