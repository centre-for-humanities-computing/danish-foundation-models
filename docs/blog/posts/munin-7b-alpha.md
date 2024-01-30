---
draft: false
date: 2024-01-11
---

# Releasing Munin 7B Alpha - A Danish LLM

We are excited to announce the release of [the first model from the Danish Foundation
Models project, nicknamed Munin 7B
Alpha](https://huggingface.co/danish-foundation-models/munin-7b-alpha). This model
represents the beginning of our research into Danish Large Language Models (LLMs),
employing [continual pre-training](https://arxiv.org/abs/2308.04014) based on the
already pre-trained [Mistral-7b-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1)
model. It has been pre-trained on the [Danish Gigaword](https://gigaword.dk/) dataset,
which has been instrumental in training various Danish BERT-style models.

<!-- more -->

This release underscores our commitment to transparency about our work and the
challenges we are facing. We want to clearly note that we expect the model to perform
suboptimally for many, if not most, applications. Our evaluations on the limited
generative Danish tasks available to us have indicated that our current training
approach may negatively impact performance on these downstream tasks, even compared to
the upstream Mistral model.

| Model Name                              	 | Overall Score 	| Danish Score 	| Norwegian Score 	| Swedish Score 	|
|-----------------------------------------	 |---------------	|--------------	|-----------------	|---------------	|
| gpt-3.5-turbo-0613                      	 | 58.52 ± 2.42	  	| 56.72 ± 2.44 	| 57.31 ± 2.37	   	| 61.54 ± 2.46	  	|
| mistralai/Mistral-7B-v0.1               	 | 40.30 ± 2.15	   	| 39.60 ± 1.94 	| 35.98 ± 2.54	   	| 45.31 ± 1.96	 	|
| **danish-foundation-models/munin-7b-alpha**| 37.50 ± 2.49  	| 39.56 ± 2.70 	| 30.82 ± 2.69    	| 42.13 ± 2.07	  	|
| AI-Sweden-Models/gpt-sw3-6.7b-v2       	 | 26.67 ± 2.30	  	| 23.65 ± 2.02	| 24.28 ± 2.74	   	| 32.08 ± 2.13	  	|
| mhenrichsen/danskgpt-tiny              	 | 16.87 ± 3.05	   	| 16.66 ± 2.18 	| 15.16 ± 2.64	   	| 18.80 ± 4.35	  	|

See [the full ScandEval leaderboard](https://scandeval.com) for an up-to-date
See [the full ScandEval
leaderboard](https://scandeval.com/mainland-scandinavian-nlu-benchmark/) for an
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
generously supported by the following:

- [Danish e-infrastructure Consortium](https://www.deic.dk/)
- [Acquisition and Logistics Organisation at the Danish Ministry of Defence](https://www.fmi.dk/)
- Danish Ministry of Higher Education and Science under [the Digital Security, Trust
  and Data Ethics performance contract](https://bedreinnovation.dk/)
