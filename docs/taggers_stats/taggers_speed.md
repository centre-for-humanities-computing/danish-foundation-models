# Statistics on Dolma and Scandi taggers

The dataset for testing is a subset of [DAGW](https://huggingface.co/datasets/DDSC/partial-danish-gigaword-no-twitter), which is only consist of documents from domain `Wiki & Books` (430837 in total). However, during testing, 161915 documents that only contains white space(s) were found out due to the `ZeroDivisionErro` in tagger `pii_regex_v1` when there is no empty documents.

Finally, the test on taggers performed on cleaned `Wiki & Books` section of DAGW (268922 in total), each following tagger was tested only once using one proccess.

Here is an example of how to use a tagger ([Detailed documentation](https://github.com/allenai/dolma/blob/main/docs/taggers.md)):

```bash
dolma tag \
    --documents "/work/github/test_on_dagw_wiki/documents/dagw_only_wiki.json.gz" \
    --experiment char_length_v1 \
    --taggers char_length_v1 \
    --processes 1
```
*Remark:*
`pii_presidio_v1` has a maximum text of length 1000000: 
```bash
dolma.core.errors.DolmaFatalError: Failed to process /work/github/test_on_dagw_wiki/documents/dagw_only_wiki.json.gz due to ValueError: [E088] Text of length 1215638 exceeds maximum of 1000000. The parser and NER models require roughly 1GB of temporary memory per 100,000 characters in the input. This means long texts may cause memory allocation errors. If you're not using the parser or NER, it's probably safe to increase the `nlp.max_length` limit. The limit is in number of characters, so you can check whether your inputs are too long by checking `len(text)`.
```

| # | Dolma Tagger | Description | Process Time (In total, Speed) |
| ---- | ---- | ---- | ---- |
| 1 | char_length_v1 | Computes document length in characters | 16s, 16.2kd/s |
| 2 | char_length_with_paragraphs_v1 | Computes document and paragraph length in characters | 49s, 5.40kd/s |
| 3 | cld2_en_doc_v2 | Detects document language using cld2 | 56s, 4.76kd/s |
| 4 | olmo_pretokenizer_v1 | Counts number of tokens using OLMo v1 pre-tokenizer | 6m57s, 645d/s |
| 5 | olmo_pretokenizer_with_paragraphs_v1 | Counts tokens in document and paragraphs using OLMo v1 pre-tokenizer | 7m02s, 636d/s |
| 6 | whitespace_tokenizer_v1 | Counts whitespace-separated tokens in document | 1m00s, 4.47kd/s |
| 7 | whitespace_tokenizer_with_paragraphs_v1 | Counts whitespace-separated tokens in document and paragraphs | 1m39s, 2.70kd/s |
| 8 | random_number_v1 | Assigns a random number to each document | 17s, 15.6kd/s |
| 9 | ft_lang_id_en_doc_v2 | Uses fastText to detect the language of the document | 2m28s, 1.82kd/s |
| 10 | ft_lang_id_en_paragraph_v2 | Uses fastText to detect the language of each paragraph | 6m21s, 705d/s |
| 11 | ft_lang_id_en_paragraph_with_doc_score_v2 | Uses fastText to detect the language of each paragraph and assigns a score based on the fraction of English paragraphs | 6m16s, 715d/s |
| 12 | gopher_v1 | Tags spans of documents matching [Deepmind's Gopher](https://arxiv.org/abs/2112.11446) removal rules | 15m49s, 283d/s |
| 13 | c4_v1 | Implements taggers used to generate the [C4](https://arxiv.org/abs/1910.10683) dataset | 3m50s, 1.17kd/s |
| 14 | c4_v2 | Faster implementation of the C4 taggers | 2m08s, 2.10kd/s |
| 15 | pii_presidio_v1 | Tags spans of documents that contain personally identifiable information (PII) using the [Presidio Analyzer](https://microsoft.github.io/presidio/analyzer/) library | way to slow: about 7s per document. However `analyzer_results` in pii.py defines the language as English if . See line 110 in [here](https://github.com/allenai/dolma/blob/main/python/dolma/taggers/pii.py#L108) |
| 16 | pii_regex_v1 | Tags spans of documents that contain personally identifiable information (PII) using a set of regular expressions | 2m55s, 1.53kd/s |
| 17 | pii_regex_v2 | Faster implementation of `pii_regex_v1` | 2m51s, 1.57kd/s |
| 18 | pii_regex_with_counts_v2 | Tags spans of documents that contain personally identifiable information (PII) using a set of regular expressions. It also counts the number of matches for each regular expression | 2m43s, 1.65kd/s |
| 19 | pii_regex_with_counts_fast_v2 | Faster implementation of `pii_regex_with_counts_v2` | 1m01s, 4.36kd/s |
| 20 | cld2_scandi_doc | Language Detection using cld2 | 1m11s, 3.79kd/s |
| 21 | cld2_scandi_paragraph | Language Detection on paragraph level using cld2 | 5m59s, 748d/s |
| 22 | ft_lang_id_scandi_doc | FastText Language Detection | 3m14s, 1.38kd/s |
| 23 | ft_lang_id_scandi_paragraph | FastText Language Detection on paragraph level | 14m06s, 318d/s |
| 24 | cld2_scandi_paragraph_with_doc_score | Language Detection on paragraph level with a total score using cld2 | 8m04s, 556d/s |
| 25 | ft_lang_id_scandi_paragraph_with_doc_score | FastText Language Detection on paragraph level with a total score | 14m37s, 306d/s |
| 26 | jigsaw_hatespeech_document_v2 | Tags documents as containing hate speech or not using a FastText classifier trained on the [Jigsaw](https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification) hate speech dataset. | 1m38s, 2.74kd/s |
| 27 | jigsaw_hatespeech_sentence_v2 | Tags spans of documents as containing hate speech or not using a FastText classifier trained on the [Jigsaw](https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification) hate speech dataset. | 9m45s, 460d/s |
| 28 | jigsaw_nsfw_document_v1 | Tags documents as containing NSFW content or not using a FastText classifier trained on the [Jigsaw](https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification) NSFW dataset. | 6m40s, 671d/s |
| 29 | jigsaw_nsfw_sentence_v2 | Tags spans of documents as containing NSFW content or not using a FastText classifier trained on the [Jigsaw](https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification) NSFW dataset. | 9m02s, 496d/s |

