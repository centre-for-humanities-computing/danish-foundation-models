
# DFM: Danish Foundation Models

[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black)](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
[![github actions pytest](https://github.com/centre-for-humanities-computing/danish-foundation-models/actions/workflows/pytest.yml/badge.svg)](https://github.com/centre-for-humanities-computing/danish-foundation-models/actions)

A collaborative project for training foundational Danish language model.

## Datasets:
The dataset currently available to the project for training:


| Dataset            | Description                                                              | Size in million tokens (filtered) | Open Source
| ------------------ | ------------------------------------------------------------------------ | ---------------------- |--------------
| :books: DAGW       | Danish Gigaword. A wide coverage dataset of Danish text.                 | \~1 000 (\~?)              | ✅
| :bird: HopeTwitter | A dataset of tweets collected as a part of the HOPE project.             | ~973 (~463)                       | ✅
| :newspaper: DaNews | A dataset consisting of Danish newspapers                                | ~9 296 (~8 667)                      | 
| 🗯 Reddit-da        | A Danish subsection of reddit                                            | ~86                   | ✅
| :link: Netarkivet  | A subsection of the "Danish" internet collected the royal Danish library | ~400 000 (~130 000)                    | 
| :link: mC4         | A cleaned part of the common crawl                                       |                        | ✅
| Lex.dk             | A Danish curated wikipedia, written by experts                           | ~26                    | 
| **Sum**             |                                                                          | ~11 381 (~9 130)                    | 



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
- [x] Jan.-Feb.: building codebase for cleaning
- [ ] Jan.-Mar.: building codebase for training
- [ ] 15th Mar.: Data cleaning done
- [ ] 1st Apr.: Dataset descriptions done
- [ ] Mar.: start training of a candidate model
- [ ] Apr.: training of model in each model category
- [ ] Maj: start training largest possible model
- [ ] 1st Maj: Larger call for project will language models

# Wish to contribute
DFM is considered a collaborate project for training and improving Danish Language models. If you wish to contribute don't hesitate to reach out using the discussion section or directly to the authors.

To get started contributing:
```
# Clone the project
git clone https://github.com/centre-for-humanities-computing/danish-foundation-models

# Install libraries
pip3 install -r requirements.txt

# Run test suite (first run will download datasets)
python3 -m pytest tests
```

# Acknowledgements
This project uses compute resources supplied by [Ucloud](https://docs.cloud.sdu.dk/index.html).

## Current Contributors:
- Kenneth Enevoldsen, Kenneth.enevoldsen@cas.au.dk
- Lasse Hansen
- Jan Kostkan
- Dan Saattrup Nielsen
- Malte Højmark-Bertelsen
- Kasper Junge
- Jens Dahl Møllerhøj
- Martin Bernstorff
- Rokas Maksevičius - Junior developer cleaning the netarkiv
- Peter Bjerregaard Vahlstrup - the guy who makes sure data collections works
- Kristoffer Nielbo - Supervisor

## FAQ

### How to I run the tests
If you are used to running
```
python -m  pytest
```

to run the test, you will notice that this does not work with the current folder setup. This is intentional as this ensures that you always run the package installation before running the tests. This removes potential errors from the installation process.

```
pip install --editable .
python -m  pytest
```
