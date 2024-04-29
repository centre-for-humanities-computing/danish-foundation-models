"""use like:
python convert_dcp_to_hf.py /flash/project_465000670/munin-7b-2024-v2-schedulefree/checkpoints/ ../../2024-v2-schedulefree/hf/ \
 --upload danish-foundation-models/munin-7b-2024-v2-schedulefree --name ep0-ba7500
"""

import argparse
import os

import torch
from torch.distributed.checkpoint import FileSystemReader
from torch.distributed.checkpoint.metadata import (
    Metadata,
    STATE_DICT_TYPE,
    TensorStorageMetadata
)
from torch.distributed.checkpoint._traverse import set_element
from torch.distributed.checkpoint.default_planner import DefaultLoadPlanner
from torch.distributed.checkpoint.state_dict_loader import _load_state_dict
from composer.models.huggingface import get_hf_config_from_composer_state_dict
from llmfoundry.utils import get_hf_tokenizer_from_composer_state_dict
import safetensors.torch

class _EmptyStateDictLoadPlanner(DefaultLoadPlanner):
    """
    Extension of DefaultLoadPlanner, which rebuilds state_dict from the saved metadata.
    Useful for loading in state_dict without first initializing a model, such as
    when converting a DCP checkpoint into a Torch save file.

    . N.B. `state_dict` must be an empty dictionary when used with this LoadPlanner

    .. warning::
        Because the entire state dict is initialized, It's recommended to only utilize
        this LoadPlanner on a single rank or process to avoid OOM.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_up_planner(
        self,
        state_dict: STATE_DICT_TYPE,
        metadata: Metadata,
        is_coordinator: bool,
    ) -> None:
        assert not state_dict

        # rebuild the state dict from the metadata
        for k, v in metadata.state_dict_metadata.items():
            if isinstance(v, TensorStorageMetadata):
                v = torch.empty(v.size, dtype=v.properties.dtype)  # type: ignore[assignment]
            if k in metadata.planner_data:
                set_element(state_dict, metadata.planner_data[k], v)
            else:
                state_dict[k] = v

        super().set_up_planner(state_dict, metadata, is_coordinator)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=str, help="Path to the source DCP model")
    parser.add_argument("dst", type=str, help="Path to the destination model")
    parser.add_argument("--name", type=str, required=True, help="name of the model")
    parser.add_argument("--type", type=str, default="hf", choices=["hf", "pt"], help="Type of the destination model")
    parser.add_argument("--upload", type=str, default=None, help="HF repo to upload to (name gets appended)")
    args = parser.parse_args()
    
    src_dir = os.path.join(args.src, args.name)
    dst_dir = os.path.join(args.dst, args.name)
    if not os.path.isdir(src_dir):
        raise RuntimeError(f"Source DCP {src_dir} does not exist")
    sd: STATE_DICT_TYPE = {}
    storage_reader = FileSystemReader(src_dir)

    _load_state_dict(
        sd,
        storage_reader=storage_reader,
        planner=_EmptyStateDictLoadPlanner(),
        no_dist=True,
    )
    if args.type == "hf":
        if 'state' not in sd:
            raise RuntimeError(
                f'"state" is not an available key in the provided composer checkpoint. Is {args.src} ill-formed?'
            )
        # Build and save HF Config
        print('#' * 30)
        print('Saving HF Model Config...')
        dtype = torch.bfloat16
        hf_config = get_hf_config_from_composer_state_dict(sd)
        hf_config.torch_dtype = dtype
        hf_config.save_pretrained(dst_dir)
        print(hf_config)

        # Extract and save the HF tokenizer
        print('#' * 30)
        print('Saving HF Tokenizer...')
        hf_tokenizer = get_hf_tokenizer_from_composer_state_dict(
            sd, trust_remote_code=False)
        if hf_tokenizer is not None:
            hf_tokenizer.save_pretrained(dst_dir)
            print(hf_tokenizer)
        else:
            print('Warning! No HF Tokenizer found!')

        # Extract the HF model weights
        print('#' * 30)
        print('Saving HF Model Weights...')
        weights_state_dict = sd
        if 'state' in weights_state_dict:
            weights_state_dict = weights_state_dict['state']['model']
        torch.nn.modules.utils.consume_prefix_in_state_dict_if_present(
            weights_state_dict, prefix='model.')

        # Convert weights to desired dtype
        for k, v in weights_state_dict.items():
            if isinstance(v, torch.Tensor):
                weights_state_dict[k] = v.to(dtype=dtype)

        # Save weights
        # torch.save(weights_state_dict, os.path.join(args.dst, 'pytorch_model.bin'))
        safetensors.torch.save_file(weights_state_dict, os.path.join(dst_dir, 'model.safetensors'))

        print('#' * 30)
        print(f'HF checkpoint folder successfully created at {args.dst}.')

        if args.upload:
            from huggingface_hub import HfApi
            api = HfApi()
            repo_id = f"{args.upload}-{args.name}"

            print(
                f'Uploading {dst_dir} to HuggingFace Hub at {repo_id}'
            )
            api.create_repo(repo_id=repo_id,
                            use_auth_token=True,
                            repo_type='model',
                            private=True,
                            exist_ok=False)
            print('Repo created.')

            api.upload_folder(folder_path=dst_dir,
                          repo_id=repo_id,
                          use_auth_token=True,
                          repo_type='model',
                          )
            print('Folder uploaded.')
    elif args.type == "pt":
        torch.save(sd, dst_dir)
    else:
        raise ValueError(f"Unknown destination type {args.type}")

