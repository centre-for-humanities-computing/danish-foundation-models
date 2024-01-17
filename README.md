

![](docs/_static/logo.png)

[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black)](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)


A collaborative project for training foundational Danish language model. Which seeks to:

- Develop and maintain **state-of-the-art models** for Danish, 
- which are **well-validated** across a wide range of tasks.
- Furthermore, we wish to **ensure good documentation**, which allows users to assess the model for their use-case critically
- **Open-source**, both model and source code

*Note*: This repository is intended for the text model of DFM.


### More information:
For more information please check out the following links:

|                                                                                                         |                                                                                                         |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 📑 [**About**](https://centre-for-humanities-computing.github.io/danish-foundation-models/)              | A overview of the DFM project                                                                           |
| [**Research Paper**](https://arxiv.org/abs/2311.07264)                                                  | An paper introducing DFM and its rationale                                                              |
| 🚀 [**Models**](https://centre-for-humanities-computing.github.io/danish-foundation-models/models_text/) | A overview of current models available through the DFM project                                          |
| 💽 [**Datasets**](https://centre-for-humanities-computing.github.io/danish-foundation-models/dcc/)       | Includes datasheets about the datasets which includes preprocessing, reason for constructions and more. |



## Danish Collosal Corpus

We currently use the Danish Colossal Corpus (DCC) version 1.1.0 to train Danish Language models. DCC consists of the following datasets: 

| Dataset                                                                                                                                       | Description                                                              | Size in billion tokens (filtered) | Version |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | --------------------------------- | ------- |
| 📚 [DAGW, Reddit]([DDSC/dagw_reddit_filtered_v1.0.0](https://huggingface.co/datasets/DDSC/dagw_reddit_filtered_v1.0.0))                        | Danish Gigaword and Reddit. DAGW includes a wide coverage dataset        | 0.83                              | v1      |
| 🐦 [HopeTwitter](https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/main/docs/datasheets/hopetwitter.md)         | A dataset of tweets collected as a part of the HOPE project.             | 0.48                              | v1      |
| 📰 [DaNews](https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/main/docs/datasheets/danews.md)                   | A dataset consisting of Danish newspapers                                | 8.67                              | v1      |
| 🌐 [Netarkivet Text](https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/main/docs/datasheets/Netarkivet_text.md) | A subsection of the "Danish" internet collected the royal Danish library | >100                              | v2      |


# Wish to contribute?
DFM is considered a collaborative project for training and maintaining Danish Language models. If you wish to contribute don't hesitate to reach out using one of the following channels:

|                                                                                                                      |                                                               |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 🗣 [**DDSC Slack**](https://join.slack.com/t/danskdatascie-o8m9638/shared_invite/zt-1jh2dwmj4-D_mjywfXERvVP75n9O0ykg) | Join the discussion in the "danish-foundation-models"-channel |
| 💬 [**GitHub Discussion**](https://github.com/centre-for-humanities-computing/danish-foundation-models/discussions)   | Ask questions or start a discussion                           |
| 🚨 [**GitHub Issues**](https://github.com/centre-for-humanities-computing/danish-foundation-models/issues)            | Notices a bug in the code? Please create an issue             |

You can contribute both:

-  Developer time, the lifeblood of any open-source project
-  Pre-training datasets you wish to include in the model training
-  Validation tasks can even be private benchmarks where you only wish to share the performance metrics.
- And probably in many other ways

## Setting up development environment
### Method 1: Dev container
By far the easiest way is to use our included development container. If you're using VSCode:

* Ensure you have either [Orbstack](https://orbstack.dev) or [Docker](https://docker.com) installed 
* Press this button: [![Open in Dev Container](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/centre-for-humanities-computing/danish-foundation-models/)
* Select "From Dockerfile"
* Press "OK" on the feature screen

### Method 2: Manual install
Install as you usually would, replicating the commands in the `Dockerfile.dev`.

## Current Contributors and Collaborators
This project has collaborators across industry, national institutions and research centers. This project uses compute resources supplied by [Ucloud](https://docs.cloud.sdu.dk/index.html) through the [DeiC e-infrastructure grant](https://www.deic.dk/en/supercomputing/Apply-for-HPC-resources).


