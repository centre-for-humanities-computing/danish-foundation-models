
# dfm-bert-base Model Card

In accordance with [1], we present the `dfm-bert-base` model card.

*Organization developing the Model*: The Danish Foundation Models project

*Model Date*: June 2022

*Model Type*: Transformer encoder model[2]; BERT [3]

*Feedback on the Model*: kenneth.enevoldsen@uni.au.dk

## Indended Uses

*Primary Intended Uses*: 

The primary intended use case of this model is reproduction and validation of dataset quality. The intended use cases for future iterations of this model is application in industry and research for Danish natural language tasks.

*Primary Intended Users*:

Future iterations of the model is intended for NLP practioners dealing with Danish text documents.

*Out-of-Scope Uses*:

Use of the model for profiling in a way which is inconsiderate of the potential harm it might cause, such as racial profiling.

## Factors

*Card prompts - Relevant Factors*:

Relevant factors include which language is used. Our model is trained on a Danish 
text corpus and is intended for comparison of the training data.

*Card prompts - Evaluation Factors*:

Future iterations of this model should include a validation of biases pertaining to gender, race as well as religous and social groups.

## Metrics

*Performance Metrics*:

Our model is evaluated on the following performance metrics:

- Pseudo perplexity, following [4], across 8 distinctly different domains including Danish dialects, books, legal, social media (Reddit, Twitter), spontaneous speech, news and wikipedia.
- The Danish subsection of Scandeval [5].

*Decision Threshold*: 

N/A

*Approaches to Uncertainty and Variability*: 

Due to the cost of training the model is only pre-trained once, but the scandeval fine-tunes 10 times to obtain a reasonable estimate of model performance.

## Evaluation Data

*Datasets*:

The ScandEval's Danish benchmark includes:

- Named entity recognition on DaNE [7,8].
- Part-of-speech tagging and dependency on DDT [8].
- Sentiment classification on AngryTweets [9], TwitterSent [9], Europarl [9], LCC [10]
- Hate speech classifcation on DKHate [11].

*Motivation*:

The Scandeval benchmark is the most comprehensive benchmark for Danish. Pseudo perplexity was analysed specifically to examine the model ability to model certain language domains.

*Pre-processing*:

Input documents is tokenized using the tokenizer of the Danish BERT by BotXO [12], which use a BPE with a vocabulary size of ~30.000 and NFKC normalization. 

## Training Data

For our training data we sample from HopeTwitter, Danews, DAGW$_{DFM}$ and Netarkivet Text (NAT) with the probabilites; 0.10, 0.10, 0.10, 0.70. For more information on the training datasets see the respective datasheets.



## Ethical Considerations

*Data*: The is sources from News, DAGW, Twitter, and Netarkivet Text (NAT) and might thus contain hate-speech, sexually explicit content and otherwise harmful content.

*Mitigations*: We considered removing sexually explicit content by filtering web domians using a DNS or using google safe-search. However, examining the filtering domains these were also found to include news media pertaining to a specific demographic (e.g. Dagens.dk) and educational sites pertaining to sexual education. We also examined the use of word-based filters, but found that might influence certain demographic groups disproportionally.

*Risk and Harms*: As Netarkivet cover such a wide array of the Danish internet it undoubtably contains personal information. To avoid model memorization of this information we have deduplicated the data such that the model does not learn this information.

# References:

- [1] Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model Cards for Model Reporting. Proceedings of the Conference on Fairness, Accountability, and Transparency, 220–229. https://doi.org/10.1145/3287560.3287596
- [2] Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention Is All You Need. ArXiv:1706.03762 [Cs]. http://arxiv.org/abs/1706.03762
- [3] Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. ArXiv:1810.04805 [Cs]. http://arxiv.org/abs/1810.04805
- [4] Salazar, J., Liang, D., Nguyen, T. Q., & Kirchhoff, K. (2020). Masked Language Model Scoring. Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, 2699–2712. https://doi.org/10.18653/v1/2020.acl-main.240
- [6] Nielsen, D. S. (2021). ScandEval: Evaluation of language models on mono- or multilingual Scandinavian language tasks. GitHub. Note: Https://Github.Com/Saattrupdan/ScandEval.
- [7] Hvingelby, R., Pauli, A. B., Barrett, M., Rosted, C., Lidegaard, L. M., & Søgaard, A. (2020). DaNE: A named entity resource for danish. Proceedings of the 12th Language Resources and Evaluation Conference, 4597–4604.
- [8] Kromann, M. T. (2003). The Danish Dependency Treebank and the DTAG Treebank Tool. https://research.cbs.dk/en/publications/the-danish-dependency-treebank-and-the-dtag-treebank-tool
- [9] Alexandrainst/danlp. (2022). Alexandra Institute. https://github.com/alexandrainst/danlp/blob/a1e9fa70fc5a3ae7ff78877062da3a8a8da80758/docs/docs/datasets.md (Original work published 2019)
- [10] Nielsen, F. Å. (2022). Lcc-sentiment. https://github.com/fnielsen/lcc-sentiment (Original work published 2016)
- [11] Sigurbergsson, G. I., & Derczynski, L. (2020). Offensive Language and Hate Speech Detection for Danish. Proceedings of the 12th Language Resources and Evaluation Conference, 3498–3508. https://aclanthology.org/2020.lrec-1.430
- [12] Møllerhøj, J. D. (2019, December 5). Danish BERT model: BotXO has trained the most advanced BERT model. BotXO. https://www.botxo.ai/blog/danish-bert-model/







