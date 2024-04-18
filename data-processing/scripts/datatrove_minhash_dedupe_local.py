from typing import Any, Union

from datatrove.executor.local import LocalPipelineExecutor
from datatrove.pipeline.dedup import MinhashDedupSignature
from datatrove.pipeline.dedup.minhash import (
    MinhashConfig,
    MinhashDedupBuckets,
    MinhashDedupCluster,
    MinhashDedupFilter,
)
from datatrove.pipeline.readers import JsonlReader
from datatrove.pipeline.tokens import TokensCounter
from datatrove.pipeline.writers.jsonl import JsonlWriter

def dolma_to_datatrove_adapter(data: dict[str, Union[str, dict[str, Any], list[Any]]], path: str, id_in_file: int | str) -> dict[str, Any]:
    """
    The default data adapter to adapt input data into the datatrove Document format

    Args:
        data: a dictionary with the "raw" representation of the data
        path: file path or source for this sample
        id_in_file: its id in this particular file or source

    Returns: a dictionary with text, id, media and metadata fields

    """
    source_dolma = data.pop("source")
    id_dolma = data.pop("id")
    assert isinstance(source_dolma, str)
    assert isinstance(id_dolma, str)

    new_id = source_dolma + "+++" + id_dolma
    return {
        "text": data.pop("text", ""),
        "id": new_id,
        "media": data.pop("media", []),
        "metadata": data.pop("metadata", {}) | data,  # remaining data goes into metadata
    }


# you can also change ngrams or the number of buckets and their size here
minhash_config = MinhashConfig(use_64bit_hashes=True)  # better precision -> fewer false positives (collisions)

BASE_DIR = "/work/dfm-data/pre-training-clean/2024-v2/datatrove_dedupe"

MINHASH_BASE_PATH = f"{BASE_DIR}/mybucket/minhash/"

MINHASH_LOGS_FOLDER = f"{BASE_DIR}/mybucket/my_minhash_logs_path/"
LOCAL_LOGS_FOLDER = f"{BASE_DIR}/my_local_folder_for_slurm_logs/"

TOTAL_TASKS = 64

# this is the original data that we want to deduplicate
INPUT_READER = JsonlReader("/work/dfm-data/pre-training-clean/2024-v2/documents/", glob_pattern="*.gz", adapter=dolma_to_datatrove_adapter)

# stage 1 computes minhash signatures for each task (each task gets a set of files)
stage1 = LocalPipelineExecutor(
    #job_name="mh1",
    pipeline=[
        INPUT_READER,
        MinhashDedupSignature(output_folder=f"{MINHASH_BASE_PATH}/signatures", config=minhash_config),
    ],
    tasks=TOTAL_TASKS,
    #time="5:00:00",
    #partition="hopper-cpu",
    logging_dir=f"{MINHASH_LOGS_FOLDER}/signatures",
    #slurm_logs_folder=f"{LOCAL_LOGS_FOLDER}/signatures/slurm_logs",
    #qos="high",
    start_method="fork",
)
stage1.run()

# stage 2 finds matches between signatures in each bucket
stage2 = LocalPipelineExecutor(
    #job_name="mh2",
    pipeline=[
        MinhashDedupBuckets(
            input_folder=f"{MINHASH_BASE_PATH}/signatures",
            output_folder=f"{MINHASH_BASE_PATH}/buckets",
            config=minhash_config,
        ),
    ],
    tasks=minhash_config.num_buckets,
    #time="90:00:00",
    #partition="hopper-prod",
    logging_dir=f"{MINHASH_LOGS_FOLDER}/buckets",
    #depends=stage1,
    #slurm_logs_folder=f"{LOCAL_LOGS_FOLDER}/buckets/slurm_logs",
    #qos="high",
    start_method="fork",
)
stage2.run()

# stage 3 creates clusters of duplicates using the results from all buckets
stage3 = LocalPipelineExecutor(
    #job_name="mh3",
    pipeline=[
        MinhashDedupCluster(
            input_folder=f"{MINHASH_BASE_PATH}/buckets",
            output_folder=f"{MINHASH_BASE_PATH}/remove_ids",
            config=minhash_config,
        ),
    ],
    tasks=1,
    #time="90:00:00",
    #partition="hopper-prod",
    logging_dir=f"{MINHASH_LOGS_FOLDER}/clusters",
    #mem_per_cpu_gb=70,
    #cpus_per_task=2,
    #depends=stage2,
    #slurm_logs_folder=f"{LOCAL_LOGS_FOLDER}/clusters/slurm_logs",
    start_method="fork",
)
stage3.run()

# stage 4 reads the original input data and removes all but 1 sample per duplicate cluster
# the data must match exactly stage 1, so number of tasks and the input source must be the same
stage4 = LocalPipelineExecutor(
    #job_name="mh4",
    pipeline=[
        INPUT_READER,
        TokensCounter(),  # nice way to see how many tokens we had before and after deduplication
        MinhashDedupFilter(
            input_folder=f"{MINHASH_BASE_PATH}/remove_ids",
            exclusion_writer=JsonlWriter(f"{MINHASH_BASE_PATH}/removed"),
        ),
        JsonlWriter(output_folder=f"{MINHASH_BASE_PATH}/deduplicated_output"),
    ],
    tasks=TOTAL_TASKS,
    #time="50:00:00",
    #partition="hopper-cpu",
    logging_dir=f"{MINHASH_LOGS_FOLDER}/filter",
    #depends=stage3,
    #slurm_logs_folder=f"{LOCAL_LOGS_FOLDER}/filter/slurm_logs",
    start_method="fork",
)
stage4.run()
