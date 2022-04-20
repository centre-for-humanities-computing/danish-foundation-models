# Plan for the test dataset

We want the test dataset to contain an equal amount of data split into various
tasks, described below.

Aside from ensuring that the resulting models perform well across multiple
tasks and do not overfit to any single one such, this would also provide
transparent performance descriptions of the trained models. Such transparency
would mean that anyone who is looking for a language model to finetune on their
dataset can immediately see whether the model works well on their domain/task.

## Tasks

As mentioned above, we want the test dataset to contain an equal amount of
data from each of the following tasks:

- Danish web data (Netarkivet)
- Danish social media data (HOPE Twitter, Reddit-da and Hestenettet from Danish
  Gigaword)
- Danish legal data (Retsinformation and Skat.dk, both from Danish Gigaword)
- Danish wiki data (Danish Wikipedia and lex.dk)
- Danish news data (DaNews)
- Danish books (Gutenberg, Danish literature, WikiBooks and WikiSource, all
  from Danish Gigaword)
- Danish spontaneous text (OpenSubtitles and Spontaneous Speech, both from
  Danish Gigaword)
- Danish dialectal data (Botxt and Sønderjysk, both from Danish Gigaword)

We would also like to test separately on other languages, to see how well it
has understood these. These only appear as separate test scores and are not
included in any aggregated test score of the model. To keep these scores
comparable, they have all been taken from the same
[OSCAR](https://ids-pub.bsz-bw.de/frontdoor/index/index/docId/9021) dataset.

- English data ([OSCAR-en](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_en/train)
- Norwegian Bokmål data ([OSCAR-nb](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_no/train))
- Norwegian Nynorsk data ([OSCAR-nn](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_nn/train))
- Swedish data ([OSCAR-sv](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_sv/train))
- Icelandic data ([OSCAR-is](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_is/train))
