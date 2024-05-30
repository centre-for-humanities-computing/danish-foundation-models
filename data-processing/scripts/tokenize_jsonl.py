import argparse
import os
import io
import orjsonl
from pathlib import Path
from transformers import AutoTokenizer
from streaming import MDSWriter
import numpy as np
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from streaming.base.util import merge_index

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def tokenize_and_write_to_mds(input_file: Path, output_dir: Path, tokenizer_name: str, bos_tokens: list[int], eos_tokens: list[int], concat_tokens: int):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    assert input_file.is_file()
    assert output_dir.is_dir()

    lines = orjsonl.stream(input_file)
    with MDSWriter(
        columns={"tokens": "ndarray"},
        out=str(output_dir),
        compression="zstd",
        size_limit=128 * 1024 * 1024,
    ) as writer:
        buffer = np.empty(0, dtype=np.uint32, order="C")
        for line in lines:
            text: str = line["text"]
            tokens = tokenizer(text, add_special_tokens=True, truncation=False, padding=False, return_tensors="np")["input_ids"]
            buffer = np.append(buffer, [*bos_tokens, *tokens, *eos_tokens])
            while len(buffer) >= concat_tokens:
                #concat_sample = buffer[:concat_tokens]
                #buffer = buffer[concat_tokens:]
                concat_sample, buffer = np.split(buffer, [concat_tokens])
                writer.write({"tokens": concat_sample})

def validate_tokenizer_settings(args):
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, use_fast=True)

    if args.bos_text is None:
        args.bos_text = ""
    if args.eos_text is None:
        args.eos_text = ""

    if args.bos_text + args.eos_text == "":
        test_tokens = tokenizer("test")
        if (
            test_tokens["input_ids"][0] != tokenizer.bos_token_id
            and test_tokens["input_ids"][-1] != tokenizer.eos_token_id
        ):
            tok_error_msg = "This tokenizer does not insert an EOS nor BOS token. "
            tok_error_msg += (
                "Concatenating with this tokenizer will result in sequences being "
            )
            tok_error_msg += (
                "attached without a separating token. Please use another tokenizer, "
            )
            tok_error_msg += (
                "such as facebook/opt-125m, or specify EOS/BOS text with e.g. "
            )
            tok_error_msg += "--bos_text=<|endoftext|>."
            raise ValueError(tok_error_msg)
        
    bos_tokens = tokenizer(
        args.bos_text, truncation=False, padding=False, add_special_tokens=False
    )["input_ids"]
    if len(bos_tokens) > 1:
        print(
            f"Your BOS text is not tokenizing to one token\
            , instead we got {bos_tokens}. Quit if this was in error."
        )

    eos_tokens = tokenizer(
        args.eos_text, truncation=False, padding=False, add_special_tokens=False
    )["input_ids"]
    if len(eos_tokens) > 1:
        print(
            f"Your EOS text is not tokenizing to one token\
            , instead we got {eos_tokens}. Quit if this was in error."
        )

    eos_text_provided = args.eos_text != ""
    bos_text_provided = args.bos_text != ""
    test_text = tokenizer("")
    if len(test_text["input_ids"]) > 0 and (eos_text_provided or bos_text_provided):
        message = (
            "both eos and bos"
            if eos_text_provided and bos_text_provided
            else ("eos_text" if eos_text_provided else "bos_text")
        )
        print(
            f"The provided tokenizer adds special tokens, but you also specified {message}. This may result "
            + "in duplicated special tokens. Please be sure this is what you intend."
        )
    return bos_tokens, eos_tokens

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tokenize a directory of .jsonl.zst files, write each to MDS, and finally merge.")
    parser.add_argument("--input_path", type=str, required=True, help="Path to the input directory")
    parser.add_argument("--concat_tokens", type=int, required=True, help="Number of tokens to concatenate")
    parser.add_argument("--tokenizer", type=str, default="mistralai/Mistral-7B-v0.1", help="Tokenizer to use")
    parser.add_argument("--output_path", type=str, required=False, default=None, help="Path to the output MDS directory")
    parser.add_argument("--bos_text", type=str, required=False, default=None, help="BOS token text")
    parser.add_argument("--eos_text", type=str, required=False, default=None, help="EOS token text")
    parser.add_argument("--num_procs", type=int, required=False, default=8, help="Number of processes to use")
    args = parser.parse_args()

    bos_tokens, eos_tokens = validate_tokenizer_settings(args)

    input_path = Path(os.path.abspath(args.input_path))
    input_files = list(input_path.glob("*.json*.*"))

    if not args.output_path:
        args.output_path = os.path.join(os.path.dirname(args.input_path), "mds")

    with ProcessPoolExecutor(max_workers=args.num_procs) as pool:
        try:
            # tokenize_and_write_to_mds(input_path, output_path, args.tokenizer, bos_tokens, eos_tokens, args.concat_tokens)
            futures = []
            for input_file in input_files:
                subdir = ''.join(os.path.basename(input_file).split(os.extsep)[:-2])
                output_path = Path(os.path.join(args.output_path, subdir)) # a subdirectory per input file
                output_path.mkdir(parents=True, exist_ok=True)
                futures.append(pool.submit(tokenize_and_write_to_mds, input_file, output_path, args.tokenizer, bos_tokens, eos_tokens, args.concat_tokens))
            for _ in tqdm(as_completed(futures), total=len(futures), desc="Tokenizing files"):
                pass
        except KeyboardInterrupt:
            print("Keyboard interrupt, exiting...")
            pool.shutdown(cancel_futures=True)
            exit(1)
    
    print("Merging MDS shards...")
    merge_index(args.output_path)


