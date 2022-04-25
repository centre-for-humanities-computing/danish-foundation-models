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
- Danish Reddit-da (Reddit-da)
- Danish Twitter data (Twitter, General Discussions from DAGW)
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
The DadsBench dataset consists of two parts: Domain-specific Danish texts, as well as web data in languages similar to Danish, where the non-Danish part is intended to evaluate the model's generalisation capabilities to adjacent languages.
The performance over the dataset is measured using perplexity. Each part is evaluated using a weighted average of the perplexities of the individual domains within the part, and the final performance is then a weighted average of the scores of each of the two parts.

## Danish Test Set


| Domain | Dataset  | Open Source | Tokens |
| ------ | -------- | ---- | ------ |
| Web    | OSCAR-da | ✅   | 25 000 |
| Social media | Reddit-da | ✅  | 25 000 |
| Social media |  Twitter, General Discussions | (only tweet ids) | 25 000 |
| Legal | Retsinformation & Skat.dk | ✅ | 25 000 |
| Clinical | PSYCOP project |  | 25 000 |
| Wiki | Danish Wikipedia | ✅ | 25 000 |
| News | DaNews | ✅ | 25 000 |
| Books | Gutenberg, Danish literature, WikiBooks and WikiSource | ✅ | 25 000 |
| Spontaneous speech | OpenSubtitles and Spontaneous Speech | ✅ | 25 000 |
| Dialects | Botxt | ✅ | 25 000 |
| Speeches | FTSpeech | ✅ | 25 000 |  
| **Sum** (sum open-souce) |  |  | 275 000 (225 000) |

## Non-Danish Test Set

| Language                 | Domain | Dataset  | Open Source | Tokens |
| ------ | ---| -------- | ---- | ------ |
| English                  | Web    | OSCAR-da | ✅          | 25 000 |
| Norwegian Bokmål         | Web    | OSCAR-nb | ✅          | 25 000 |
| Norwegian Nynorsk        | Web    | OSCAR-nn | ✅          | 25 000 |
| Swedish                  | Web    | OSCAR-sv | ✅          | 25 000 |
| Icelandic                | Web    | OSCAR-is | ✅          | 25 000 |
| **Sum** (sum open-souce) |        |          |             | 125 000 (125 000) |

