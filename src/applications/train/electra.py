"""
ELECTRA (replaced token detection objective)
see details in paper [ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators]
(https://arxiv.org/abs/2003.10555)

"""
from collections.abc import Mapping
from typing import Any, Dict, List, Union

import torch
import wandb
from datasets import load_dataset
from torch import nn
from transformers import (
    DataCollatorForLanguageModeling,
    ElectraConfig,
    ElectraForMaskedLM,
    ElectraForPreTraining,
    ElectraTokenizerFast,
    PretrainedConfig,
    PreTrainedModel,
    Trainer,
)
from transformers.data.data_collator import _torch_collate_batch
from transformers.utils import is_apex_available
from transformers.utils.import_utils import is_sagemaker_mp_enabled
if is_sagemaker_mp_enabled():
    from transformers.trainer_pt_utils import smp_forward_backward
if is_apex_available():
    from apex import amp


class ELECTRAModel(PreTrainedModel):
    def __init__(self, generator, discriminator, config, **kwargs):
        super().__init__(config, **kwargs)
        self.generator, self.discriminator = generator, discriminator
        self.gumbel_dist = torch.distributions.gumbel.Gumbel(0.0, 1.0)
        self.pad_token_id = config.pad_token_id

    def to(self, *args, **kwargs):
        "Also set dtype and device of contained gumbel distribution if needed"
        super().to(*args, **kwargs)
        a_tensor = next(self.parameters())
        device, dtype = a_tensor.device, a_tensor.dtype
        dtype = torch.float32
        self.gumbel_dist = torch.distributions.gumbel.Gumbel(
            torch.tensor(0.0, device=device, dtype=dtype),
            torch.tensor(1.0, device=device, dtype=dtype),
        )


    # N.B.: removed "sentA_lenths" -- didn't figure out what it was for
    def forward(
        self, input_ids, is_mlm_applied, labels, attention_mask, token_type_ids
    ):
        """
        masked_inputs (Tensor[int]): (B, L)
        sentA_lenths (Tensor[int]): (B, L)
        is_mlm_applied (Tensor[boolean]): (B, L), True for positions chosen by mlm probability
        labels (Tensor[int]): (B, L), -100 for positions where are not mlm applied
        """
        gen_logits = self.generator(input_ids, attention_mask, token_type_ids)[
            0
        ]  # (B, L, vocab size)
        # reduce size to save space and speed
        mlm_gen_logits = gen_logits[is_mlm_applied, :]  # ( #mlm_positions, vocab_size)

        with torch.no_grad():
            # sampling
            pred_toks = self.sample(mlm_gen_logits)  # ( #mlm_positions, )
            # produce inputs for discriminator
            generated = input_ids.clone()  # (B,L)
            generated[is_mlm_applied] = pred_toks  # (B,L)
            # produce labels for discriminator
            is_replaced = is_mlm_applied.clone()  # (B,L)
            is_replaced[is_mlm_applied] = pred_toks != labels[is_mlm_applied]  # (B,L)

        disc_logits = self.discriminator(generated, attention_mask, token_type_ids)[
            0
        ]  # (B, L)

        # N.B.: casting to bool here may slow down the process (not sure how much)
        return (
            mlm_gen_logits,
            generated,
            disc_logits,
            is_replaced,
            attention_mask.to(bool),
            is_mlm_applied,
        )

    def sample(self, logits):
        "Reimplement gumbel softmax cuz there is a bug in torch.nn.functional.gumbel_softmax when fp16 (https://github.com/pytorch/pytorch/issues/41663). Gumbel softmax is equal to what official ELECTRA code do, standard gumbel dist. = -ln(-ln(standard uniform dist.))"
        gumbel = self.gumbel_dist.sample(logits.shape).to(logits.device)
        return (logits.float() + gumbel).argmax(dim=-1)


class ELECTRALoss:
    def __init__(
        self, loss_weights=(1.0, 50.0), gen_label_smooth=False, disc_label_smooth=False
    ):
        self.loss_weights = loss_weights
        self.gen_loss_fc = nn.CrossEntropyLoss(label_smoothing=gen_label_smooth)
        self.disc_loss_fc = nn.BCEWithLogitsLoss()
        self.disc_label_smooth = disc_label_smooth

    def __call__(self, pred, targ_ids):
        (
            mlm_gen_logits,
            generated,
            disc_logits,
            is_replaced,
            non_pad,
            is_mlm_applied,
        ) = pred
        gen_loss = self.gen_loss_fc(mlm_gen_logits.float(), targ_ids[is_mlm_applied])
        disc_logits = disc_logits.masked_select(non_pad)  # -> 1d tensor
        is_replaced = is_replaced.masked_select(non_pad)  # -> 1d tensor
        if self.disc_label_smooth:
            is_replaced = is_replaced.float().masked_fill(
                ~is_replaced, self.disc_label_smooth
            )
        disc_loss = self.disc_loss_fc(disc_logits.float(), is_replaced.float())
        return gen_loss * self.loss_weights[0] + disc_loss * self.loss_weights[1], gen_loss * self.loss_weights[0], disc_loss * self.loss_weights[1]


class ElectraDataCollator(DataCollatorForLanguageModeling):
    def __init__(
        self,
        tokenizer,
        mlm_probability=0.15,
        replace_prob=0.1,
        original_prob=0.1,
        ignore_index=-100,
        for_electra=False,
    ):
        super().__init__(tokenizer)
        self.mlm_probability = mlm_probability
        self.replace_prob = replace_prob
        self.original_prob = original_prob
        self.ignore_index = ignore_index
        self.for_electra = for_electra

    def torch_call(
        self, examples: List[Union[List[int], Any, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        # Handle dict or lists with proper padding and conversion to tensor.
        if isinstance(examples[0], Mapping):
            batch = self.tokenizer.pad(
                examples,
                return_tensors="pt",
                pad_to_multiple_of=self.pad_to_multiple_of,
            )
        else:
            batch = {
                "input_ids": _torch_collate_batch(
                    examples, self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of
                )
            }

        # If special token mask has been preprocessed, pop it from the dict.
        special_tokens_mask = batch.pop("special_tokens_mask", None)
        if self.mlm:
            (
                batch["input_ids"],
                batch["labels"],
                batch["is_mlm_applied"],
            ) = self.torch_mask_tokens(
                batch["input_ids"], special_tokens_mask=special_tokens_mask
            )
        else:
            labels = batch["input_ids"].clone()
            if self.tokenizer.pad_token_id is not None:
                labels[labels == self.tokenizer.pad_token_id] = -100
            batch["labels"] = labels
        return batch

    def torch_mask_tokens(
        self,
        inputs,
        special_tokens_mask,
    ):
        """
        Prepare masked tokens inputs/labels for masked language modeling: (1-replace_prob-orginal_prob)% MASK, replace_prob% random, orginal_prob% original within mlm_probability% of tokens in the sentence.
        * ignore_index in nn.CrossEntropy is default to -100, so you don't need to specify ignore_index in loss
        """
        device = inputs.device
        labels = inputs.clone()

        mask_token_index = self.tokenizer.mask_token_id
        special_token_indices = self.tokenizer.all_special_ids
        vocab_size = self.tokenizer.vocab_size

        # Get positions to apply mlm (mask/replace/not changed). (mlm_probability)
        probability_matrix = torch.full(
            labels.shape, self.mlm_probability, device=device
        )
        special_tokens_mask = torch.full(
            inputs.shape, False, dtype=torch.bool, device=device
        )
        for sp_id in special_token_indices:
            special_tokens_mask = special_tokens_mask | (inputs == sp_id)
        probability_matrix.masked_fill_(special_tokens_mask, value=0.0)
        mlm_mask = torch.bernoulli(probability_matrix).bool()
        labels[
            ~mlm_mask
        ] = self.ignore_index  # We only compute loss on mlm applied tokens

        # mask  (mlm_probability * (1-replace_prob-orginal_prob))
        mask_prob = 1 - self.replace_prob - self.original_prob
        mask_token_mask = (
            torch.bernoulli(torch.full(labels.shape, mask_prob, device=device)).bool()
            & mlm_mask
        )
        inputs[mask_token_mask] = mask_token_index

        # replace with a random token (mlm_probability * replace_prob)
        if int(self.replace_prob) != 0:
            rep_prob = self.replace_prob / (self.replace_prob + self.orginal_prob)
            replace_token_mask = (
                torch.bernoulli(
                    torch.full(labels.shape, rep_prob, device=device)
                ).bool()
                & mlm_mask
                & ~mask_token_mask
            )
            random_words = torch.randint(
                vocab_size, labels.shape, dtype=torch.long, device=device
            )
            inputs[replace_token_mask] = random_words[replace_token_mask]

        # do nothing (mlm_probability * orginal_prob)

        return inputs, labels, mlm_mask


class ElectraTrainer(Trainer):
    # Might be needed if we want to move stuff up from the init below
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.data_collator = ...

    def training_step(self, model, inputs):
        model.train()
        inputs = self._prepare_inputs(inputs)

        if is_sagemaker_mp_enabled():
            loss_mb = smp_forward_backward(model, inputs, self.args.gradient_accumulation_steps)
            return loss_mb.reduce_mean().detach().to(self.args.device)

        with self.compute_loss_context_manager():
            loss, gen_loss, disc_loss = self.compute_loss(model, inputs)
        self.gen_loss = gen_loss
        self.disc_loss = disc_loss

        wandb.log({"train/gen_loss" : gen_loss})
        wandb.log({"train/disc_loss" : disc_loss})

        if self.args.n_gpu > 1:
            loss = loss.mean()  # mean() to average on multi-gpu parallel training

        if self.args.gradient_accumulation_steps > 1 and not self.deepspeed:
            # deepspeed handles loss scaling by gradient_accumulation_steps in its `backward`
            loss = loss / self.args.gradient_accumulation_steps

        if self.do_grad_scaling:
            self.scaler.scale(loss).backward()
        elif self.use_apex:
            with amp.scale_loss(loss, self.optimizer) as scaled_loss:
                scaled_loss.backward()
        elif self.deepspeed:
            # loss gets scaled under gradient_accumulation_steps in deepspeed
            loss = self.deepspeed.backward(loss)
        else:
            loss.backward()

        return loss.detach()


    def compute_loss(self, model, inputs, return_outputs=False, return_all_losses=True):
        labels = inputs.get("labels")
        # forward pass
        outputs = model(**inputs)

        loss_fct = ELECTRALoss(gen_label_smooth=False, disc_label_smooth=False)
        combined_loss, gen_loss, disc_loss = loss_fct(outputs, labels)
        if return_outputs:
            return (combined_loss, outputs)
        elif return_all_losses:
            return combined_loss, gen_loss, disc_loss
        else:
            return combined_loss


if __name__ == "__main__":
    disc_config = ElectraConfig.from_pretrained(f"google/electra-small-discriminator")
    gen_config = ElectraConfig.from_pretrained(f"google/electra-small-generator")
    generator = ElectraForMaskedLM(gen_config)
    discriminator = ElectraForPreTraining(disc_config)

    discriminator.electra.embeddings = generator.electra.embeddings
    hf_tokenizer = ElectraTokenizerFast.from_pretrained(
        f"google/electra-small-generator"
    )

    collator = ElectraDataCollator(
        tokenizer=hf_tokenizer,
        mlm_probability=0.15,
        replace_prob=0.1,
        original_prob=0.1,
        for_electra=True,
    )

    electra_model = ELECTRAModel(
        generator,
        discriminator,
        PretrainedConfig(pad_token_id=hf_tokenizer.pad_token_id),
    )

    # using some random data to test that it works
    dataset = load_dataset("glue", "cola", split="train", streaming=False)

    def group_texts(examples):
        tokenized_inputs = hf_tokenizer(
            examples["sentence"],
            return_special_tokens_mask=False,
            truncation=True,
            max_length=hf_tokenizer.model_max_length,
        )
        return tokenized_inputs

    # preprocess dataset
    tokenized_dataset = dataset.map(
        group_texts, batched=True, remove_columns=["sentence", "idx", "label"]
    )

    trainer = ElectraTrainer(
        electra_model,
        tokenizer=hf_tokenizer,
        train_dataset=tokenized_dataset,
        data_collator=collator,
    )

    trainer.train()
    trainer.save_model("model")
