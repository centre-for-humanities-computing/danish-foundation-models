
# DFM: Danish Foundation Models

[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black)](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
[![github actions pytest](https://github.com/centre-for-humanities-computing/danish-foundation-models/actions/workflows/pytest.yml/badge.svg)](https://github.com/kennethenevoldsen/asent/actions)

A collaborative project for training foundational Danish language model.

## Datasets:
The dataset currently available to the project for training:


| Dataset | Description | Size in million tokens |
| ------- | ------- | ------- |
| :books: DAGW    | Danish Gigaword. A wide coverage dataset of Danish text. | ~1 000 |
| :bird: HopeTwitter    | A dataset of tweets collected as a part of the HOPE project. | |
| :newspaper: DaNews | A dataset consisting of Danish newspapers | |
| 🗯 Reddit-da | A Danish subsection of reddit  | ~86 | 
| :link: Netarkivet | A subsection of the "Danish" internet collected the royal Danish library | | 
| :link: mC4 | A cleaned part of the common crawl | | 
| Lex.dk | A Danish curated wikipedia, written by experts | ~26 |


## Models:
Currently the plan is to train:

- An encoder model (e.g. BERT), probably DeBERTa v3
- A decoder model (like GPT3), probably GPT
- A encoder-decoder model (e.g. T5), probably T5 v1.1

Potentially other models, which might be included include:
- long-range transformers
- distilled versions of the models

### Tokenizers
Tokenizers is trained on a subset of the dataset which is chosen to be a balanced set. Currently this include
- DAGW (~1000 million tokens)
- Reddit (~85 million tokens)
- HopeTwitter (~300 million tokens)
- DaNews (~300 million tokens)

It is currently noticably missing webdata.

## Timeline:
- [x] Dec.: first meeting
- [ ] Jan.-Feb: start training of a candidate model of dataset excluding Netarkivet
- [ ] Jan.-Feb.: Finalize on a collaborate method for training the models
- [ ] Jan.: start cleaning netarkivet
- [ ] Feb.: training of candidate model in each model category
- [ ] 1st Mar.: Data cleaning done
- [ ] Mar-Apr.: start training largest model
- [ ] 1st Apr.: Larger call for project will language models
- [ ] (undated): Fine-tune model on news and twitter

# Wish to contribute
DFM is considered a collaborate project for training and improving Danish Language models. If you wish to contribute don't hesitate to reach out using the discussion section or directly to the authors.

# Acknowledgements
This project uses compute resources supplied by [Ucloud](https://docs.cloud.sdu.dk/index.html).

## Current Contributors:
- Kenneth Enevoldsen, Kenneth.enevoldsen@cas.au.dk
- Lasse Hansen
- Jan Kostkan
- Dan Saattrup Nielsen
- Malte Højmark-Bertelsen
- Kasper Junge
- Rokas Maksevičius - Junior developer cleaning the netarkiv
- Peter Bjerregaard Vahlstrup - the guy who makes sure data collections works
- Kristoffer Nielbo - Supervisor


