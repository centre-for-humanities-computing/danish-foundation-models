
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

<!-- Add which folder to mount -->

```
pip install "jax[cuda11_cudnn82]" -f https://storage.googleapis.com/jax-releases/jax_releases.html
# impossible to specify in setup.cfg:
# see https://stackoverflow.com/questions/57689387/equivalent-for-find-links-in-setup-py

# install dfm
pip install -e .[ucloud_gpu]
```

Create model repository
```
huggingface-cli login
huggingface-cli repo create dfm-bert-base
```

Next we clone the model repository to add the tokenizer and model files.
```
cd  /work/models/transformers
git clone https://huggingface.co/<your-username>/dfm-bert-base
```

To ensure that all tensorboard traces will be uploaded correctly, we need to track them. You can run the following command inside your model repo to do so.
```
cd dfm-bert-base
git lfs track "*tfevents*"
cd ..
```
We will need to move the config from the DFM repository to the model repository:

```python
from transformers import BertTokenizerFast, BertConfig

model_dir = "./dfm-bert-base"

tokenizer = BertTokenizerFast.from_pretrained("Maltehb/danish-bert-botxo")
config = BertConfig.from_pretrained("Maltehb/danish-bert-botxo")

tokenizer.save_pretrained(model_dir)
config.save_pretrained(model_dir)
```

<!-- 
Using a custom config:
```
cp /work/danish-foundation-models/configs/debertav2-config_small.json ./dfm-debertav2-small/config.json
```
Similar for the tokenizer:
```
cp /work/models/tokenizers/dfm_tokenizer/unigram_5000000_docs_128000_tokens/tokenizer.json ./dfm-debertav2-small
```
-->
To allow for comparison we with the Danish BERT by botXO (now renamed Certainly.io). 
We try to keep as many training similar to the parameters of the original implementation.
With changes to batch size and maximum training sequence (to 512).
Where BotXO doesn't report its training parameters we use those of reported in the BERT paper.

<!--
Botxo BERT hyperparameters:
```
Batch size: 1280
Max predictions per training sentence: 20
Max training sentence length: 256
Probability of masking word in training sentence: 0.15
Learning rate: 2e-5
Training steps: 1.000.000
A custom BPE vocabulary of 32.000 tokens.
```
-->

```bash
python3 /work/danish-foundation-models/src/applications/train/run_mlm_flax_stream.py \
    --output_dir=/work/models/transformers/dfm-bert-base \
    --model_type=bert \
    --config_name=/work/models/transformers/dfm-bert-base \
    --tokenizer_name=/work/models/transformers/dfm-bert-base \
    --dataset_name=dcc-v1 \
    --max_seq_length=512 \
    --per_device_train_batch_size=48 \
    --per_device_eval_batch_size=48 \
    --learning_rate=2e-5 \
    --warmup_steps=10000 \
    --overwrite_output_dir \
    --adam_beta1=0.9 \
    --adam_beta2=0.999 \
    --num_train_steps=1500000 \
    --num_eval_samples=50000 \
    --logging_steps=500 \
    --eval_steps=20000 \
    --push_to_hub \
    --weight_decay=0.01
```
- running with 90% works with batch size = 4. Seems to work, but GPU utilization 42 %
- disabling os.environ['XLA_PYTHON_CLIENT_MEM_FRACTION']='.90' and running again. This shouldn't really do anything. Also works just fine
- Increasing batch size to 16 (from 4): works just fine
- Increasing batch size to 32: works just fine
2*32*512*2,68 tokens pr. second
32 000 000 000/(2*32*512*2,68) seconds to go through 32 B tokens (what they used for t5)
32000000000/(2*32*512*2,68)/60/60/24=4.2 days to train 1 BERT-base on 2 A100 

- Increasing batch size to 64: OOM error
- decreasing batch size to 48: Works
32000000000/(2*48*512*2,00)/60/60/24=3.8 days to train 1 BERT-base on 2 A100 
- Increasign batch to 56: OOM
- decreasing to 52: OOM
- Using batch size 48, change to 4 GPUs: work

32000000000/(4*32*512*1,76)/60/60/24=3.2 days

**TODO**: 
- Tune batch size (larger gpu cluster)
- [ ] tune eval step
- [ ] tune_max_train steps

num_eval_samples = 50000




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
