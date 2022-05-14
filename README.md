
# DFM: Danish Foundation Models

[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black)](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
[![github actions pytest](https://github.com/centre-for-humanities-computing/danish-foundation-models/actions/workflows/pytest.yml/badge.svg)](https://github.com/centre-for-humanities-computing/danish-foundation-models/actions)

A collaborative project for training foundational Danish language model.

## Datasets:
The dataset currently available to the project for training:


| Dataset            | Description                                                              | Size in million tokens | Open Source?
| ------------------ | ------------------------------------------------------------------------ | ---------------------- |--------------
| :books: DAGW       | Danish Gigaword. A wide coverage dataset of Danish text.                 | ~1 000                 | Yes
| :bird: HopeTwitter | A dataset of tweets collected as a part of the HOPE project.             |                        | Yes
| :newspaper: DaNews | A dataset consisting of Danish newspapers                                |                        | No
| 🗯 Reddit-da        | A Danish subsection of reddit                                            | ~86                   | Yes
| :link: Netarkivet  | A subsection of the "Danish" internet collected the royal Danish library |                        | No
| :link: mC4         | A cleaned part of the common crawl                                       |                        | Yes
| Lex.dk             | A Danish curated wikipedia, written by experts                           | ~26                    | No


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

# How to train on UCloud

To setup to train in UCloud select the instance Coder CUDA v1.64.2 and install dependencies using:

```
pip install -e .[ucloud_gpu]
pip install "jax[cuda11_cudnn82]" -f https://storage.googleapis.com/jax-releases/jax_releases.html
# impossible to specify in setup.cfg:
# see https://stackoverflow.com/questions/57689387/equivalent-for-find-links-in-setup-py
```

Run the training script
```
python3 src/dfm/train/run_mlm_flax_stream.py 
    --output_dir=/work/models/debertav2_small 
    --model_type="debertav2"
    --config_name=/work/models/debertav2_small
    --tokenizer_name=/work/models/tokenizers/tokenizers.json
    --dataset_name="oscar"
    --dataset_config_name="unshuffled_deduplicated_en"
    --max_seq_length="128"
    --per_device_train_batch_size="128"
    --per_device_eval_batch_size="128"
    --learning_rate="3e-4"
    --warmup_steps="1000"
    --overwrite_output_dir
    --adam_beta1="0.9"
    --adam_beta2="0.98"
    --num_train_steps="10000"
    --num_eval_samples="5000"
    --logging_steps="250"
    --eval_steps="1000"
    --push_to_hub
```

```
python3 /work/danish-foundation-models/src/dfm/train/run_mlm_flax_stream.py \
    --output_dir=/work/48847/debertav2_small \
    --model_type="debertav2" \
    --config_name=/work/48847/debertav2_small \
    --tokenizer_name=/work/48847/tokenizers/tokenizers.json \
    --dataset_name="oscar" \
    --dataset_config_name="unshuffled_deduplicated_en" \
    --max_seq_length="128" \
    --per_device_train_batch_size="128" \
    --per_device_eval_batch_size="128" \
    --learning_rate="3e-4" \
    --warmup_steps="1000" \
    --overwrite_output_dir \
    --adam_beta1="0.9" \
    --adam_beta2="0.98" \
    --num_train_steps="10000" \
    --num_eval_samples="5000" \
    --logging_steps="250" \
    --eval_steps="1000" \
    --push_to_hub 
```

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
