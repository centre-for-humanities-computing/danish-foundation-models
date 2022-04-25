# DadsBench: DAnish Domain-Specific language modelling Benchmark (DadsBench) v.1

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

- Danish web data (OSCAR-da)
- Danish social media data (Twitter, General Discussions from DAGW and Reddit-da)
- Danish legal data (Retsinformation and Skat.dk, both from Danish Gigaword)
- Danish clinical data (PSYCOP,  Electronic psychiatric records)
- Danish wiki data (Danish Wikipedia and lex.dk)
- Danish news data (DaNews)
- Danish books (Gutenberg, Danish literature, WikiBooks and WikiSource, all
  from Danish Gigaword)
- Danish spontaneous text (OpenSubtitles and Spontaneous Speech, both from
  Danish Gigaword)
- Danish dialectal data (Botxt, from Danish Gigaword)
- Danish speeches (FTSpeech)

We would also like to test separately on other languages, to see how well it
has understood these. These only appear as separate test scores and are not
included in any aggregated test score of the model. To keep these scores
comparable, they have all been taken from the same
[OSCAR](https://ids-pub.bsz-bw.de/frontdoor/index/index/docId/9021) dataset.

- English data ([OSCAR-en](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_en/train))
- Norwegian Bokmål data ([OSCAR-nb](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_no/train))
- Norwegian Nynorsk data ([OSCAR-nn](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_nn/train))
- Swedish data ([OSCAR-sv](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_sv/train))
- Icelandic data ([OSCAR-is](https://huggingface.co/datasets/oscar/viewer/unshuffled_deduplicated_is/train))

### The dataset:
The DadsBench dataset consist of two main datasets. The Danish  set and a non-danish set consisting of example Non-danish set intended to model the generalizability of the model to adjacent languages.
The performance over the dataset is measures using perplexity which is calcuted pr. subset then averages across domain and then across each of the two subset resulting in two scores, one for Danish and one non-Danish languages.

## Danish Test Set


| Domain | Dataset  | Open Source | Tokens |
| ------ | -------- | ---- | ------ |
| Web    | OSCAR-da | ✅   | 25 000 |
| Social media | Reddit-da,  Twitter, General Discussions  | ✅  | 25 000 |
| Social media |  Twitter, General Discussions | (only tweet ids) | 25 000 |
| Legal | Retsinformation & Skat.dk | ✅ | 25 000 |
| Clinical | PSYCOP project |  | 25 000 |
| Wiki | Danish Wikipedia | ✅ | 25 000 |
| News | DaNews |✅ | 25 000 |
| Books | Gutenberg, Danish literature, WikiBooks and WikiSource |✅ | 25 000 |
| spontaneous speech | OpenSubtitles and Spontaneous Speech |✅ | 25 000 |
| Dialects | Botxt |✅ | 25 000 |
| Speeches | FTSpeech | ✅ | 25 000 |  
| **Sum** (sum open-souce) |  |  | 275 000 (225 000) |

## Non-danish Test Set

| Language                 | Domain | Dataset  | Open Source | Tokens |
| ------ | ---| -------- | ---- | ------ |
| English                  | Web    | OSCAR-da | ✅          | 25 000 |
| Norwegian Bokmål         | Web    | OSCAR-nb | ✅          | 25 000 |
| Norwegian Nynorsk        | Web    | OSCAR-nn | ✅          | 25 000 |
| Swedish                  | Web    | OSCAR-sv | ✅          | 25 000 |
| Icelandic                | Web    | OSCAR-is | ✅          | 25 000 |
| **Sum** (sum open-souce) |        |          |             | 125 000 (125 000) |

