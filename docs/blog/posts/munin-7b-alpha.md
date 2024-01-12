---
draft: false
date: 2024-01-11
---

# Releasing Munin 7B Alpha - A Danish LLM

We are excited to announce the release of the first model from the Danish Foundation
Models project, nicknamed Munin 7B Alpha. This model represents the beginning of our
research into Danish Large Language Models (LLMs), employing [continual
pre-training](https://arxiv.org/abs/2308.04014) based on the already pre-trained
[Mistral-7b-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1) model. It has been
pre-trained on the [Danish Gigaword](https://gigaword.dk/) dataset, which has been
instrumental in training various Danish BERT-style models.

<!-- more -->

This release underscores our commitment to transparency about our work and the
challenges we are facing. We want to clearly note that we expect the model to perform
suboptimally for many, if not most, applications. Our evaluations on the limited
generative Danish tasks available to us have indicated that our current training
approach may negatively impact performance on these downstream tasks, even compared to
the upstream Mistral model.

| Model Name                              	| Overall Score 	| Danish Score 	| Norwegian Score 	| Swedish Score 	|
|-----------------------------------------	|---------------	|--------------	|-----------------	|---------------	|
| gpt-4-0613                              	| 62.54 ± 2.87  	| 56.78 ± 2.56 	| 62.95 ± 3.63    	| 67.90 ± 2.43  	|
| gpt-3.5-turbo-0613                      	| 56.18 ± 2.84  	| 51.73 ± 2.60 	| 54.30 ± 2.86    	| 62.52 ± 3.05  	|
| mistralai/Mistral-7B-v0.1               	| 30.86 ± 2.52	   	| 27.74 ± 2.38 	| 27.26 ± 2.76	   	| 37.59 ± 2.43	 	|
| danish-foundation-models/munin-7b-alpha 	| 21.46 ± 2.98  	| 20.53 ± 2.82 	| 14.59 ± 3.47    	| 29.25 ± 2.66  	|
| mhenrichsen/danskgpt-tiny              	| 02.95 ± 1.18	  	| 01.77 ± 1.48 	| 02.63 ± 0.61	   	| 04.46 ± 1.46	  	|

See [the full ScandEval
leaderboard](https://scandeval.github.io/mainland-scandinavian-nlu-benchmark/) for an
up-to-date comparison. Despite these challenges, we hope that our open approach
encourages the community to collaborate with us in building the best possible Danish
LLM. While the current version of the model may not yet be a practical tool for Danish
NLP, we believe that sharing our findings is valuable. A critical need has been
identified: access to a significantly larger corpus of Danish text data, and a legal
framework that reliably allows for training and releasing open models, including for
commercial use.

At Danish Foundation Models, we are actively pursuing legal access to extensive Danish
text data, and are exploring every option for releasing models under the
most open license possible. We have already secured agreements that provide us access
to several large Danish datasets, and we plan to include these into our training
process in the near future.

In summary, Munin 7B Alpha is a small step forward. It signifies our commitment to
advancing Danish NLP and acknowledges the extensive work ahead. By sharing this model,
we aim to foster collaborative efforts within the community. The model is now available
for download and experimentation, and we look forward to your insights and discussions
on how we can progress.

The development of this model, and the Danish Foundation Models project in general, is
generously supported by both [Danish e-infrastructure Consortium](https://www.deic.dk/)
and [the Danish Defence](https://www.forsvaret.dk/).
