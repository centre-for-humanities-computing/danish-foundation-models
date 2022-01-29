# Pretraining a model

1. identify the appropriate script to run. For masked language modelling, use `run_mlm.py`. This includes the following models, which can be passed as the `model_type` argument. 

```
('yoso',
 'nystromformer',
 'qdqbert',
 'fnet',
 'perceiver',
 'rembert',
 'roformer',
 'big_bird',
 'wav2vec2',
 'convbert',
 'ibert',
 'mobilebert',
 'distilbert',
 'albert',
 'camembert',
 'xlm-roberta-xl',
 'xlm-roberta',
 'mbart',
 'megatron-bert',
 'mpnet',
 'bart',
 'reformer',
 'longformer',
 'roberta',
 'deberta-v2',
 'deberta',
 'flaubert',
 'squeezebert',
 'bert',
 'xlm',
 'electra',
 'funnel',
 'layoutlm',
 'tapas')
 ```

For causal language modelling, use `run_clm.py`. This supports the following models:

```
('xglm',
 'qdqbert',
 'trocr',
 'gptj',
 'rembert',
 'roformer',
 'bigbird_pegasus',
 'gpt_neo',
 'big_bird',
 'speech_to_text_2',
 'blenderbot-small',
 'bert-generation',
 'camembert',
 'xlm-roberta-xl',
 'xlm-roberta',
 'pegasus',
 'marian',
 'mbart',
 'megatron-bert',
 'bart',
 'blenderbot',
 'reformer',
 'roberta',
 'bert',
 'openai-gpt',
 'gpt2',
 'transfo-xl',
 'xlnet',
 'xlm-prophetnet',
 'prophetnet',
 'xlm',
 'ctrl',
 'electra')
```

Both `run_mlm.py` and `run_clm.py` are pytorch based. To pretrain a T5 model we need JAX and FLAX install and to run the `run_t5_mlm_flax.py` script. 


 2. Create a `{your_model}_config.json`.