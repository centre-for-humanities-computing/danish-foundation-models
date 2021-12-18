# danish-foundation-models
A project for training foundational Danish language model.

# Status:
This is an outline of the current status of the project and the responsibilities of each person. There is likely things you wish to change do let me know.

## Datasets:
- :books: DAGW: @Lasse Hansen has converted DAGW to HF format, and will perform some dedup on the dataset. We are messaging with Leon to publish both the cleaned and current version on HF datasets
- :bird: HopeTwitter: A dataset of tweets collected as a part of the HOPE project.
- :newspaper: Infomedia: @Kostkan Jan have cleaned the Infomedia corpus and is working on creating a HF version of the dataset.
- :link: Netarkivet:@Kenneth Enevoldsen will get a datadumb on UCloud. Me, Rokas (joining us mid Jan.) and @Kasper Junge will work on developing script for cleaning this data.
- 🗯 Reddit: The [reddit dataset](https://huggingface.co/datasets/DDSC/reddit-da) available on Huggingface supplied by @saatrupdan.


## Models:
- Tokenizers: @Dan my idea was simply to train all three and test which was was best using a small bert on DAGW, seems like you are already doing that. Do you need any help with this?
- Training scripts: @Malte Højmark-Bertelsen can you make an (rough) initial outline for a HF trainer using wandb sweeps?
- Model configs: (None responsible) Thinking of the categories small, medium large. With the models ELECTRA, T5 og GPT. Potentially with a few tweaks (e.g. this paper indicates potential benefits of changing activation functions).
  - @Malte Højmark-Bertelsen suggested [DeBERTa v3](https://arxiv.org/abs/2111.09543?context=cs)instead of ELECTRA


## Timeline:
- Dec.: start training of a candidate model of dataset excluding Netarkivet
- Dec.: first meeting if possible, @Kenneth Enevoldsen will send out an invite
- Jan.-feb.: Finalize on a collaborate method for training the models
- Jan.: start cleaning netarkivet
- Feb.: training of candidate model in each model category
- 1st Mar.: Data cleaning done
- Mar.: start training largest encoder model
- 1st Apr.: Larger call for project will language models
- (undated): Fine-tune model on news and twitter


# Info
- This project uses compute resources supplied by [Ucloud](https://docs.cloud.sdu.dk/index.html).

## Current collaborators:
- Kenneth Enevoldsen
- Lasse Hansen
- Jan Kostkan
- Dan Saattrup Nielsen
- Malte Højmark-Bertelsen
- Kasper Junge
- Rokas Maksevičius - Junior developer cleaning the netarkiv
- Peter Bjerregaard Vahlstrup - the guy who makes sure data collections works
- Kristoffer Nielbo - Supervisor

