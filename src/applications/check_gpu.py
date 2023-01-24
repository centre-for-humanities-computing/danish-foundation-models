"""
A small script which checks if the GPU utilization is non-zero for more than 30 minutes
if it is non-zero for more than a specified time, it will an alert to slack using weight and
biases
"""
import datetime
import subprocess
import time
from typing import List

import wandb
from wandb import AlertLevel


def get_server_name():
    """
    get name of server and user in a user@server format.
    """
    user = subprocess.run("whoami", shell=True, capture_output=True)
    user = user.stdout.decode("utf-8").strip()
    server = subprocess.run("hostname", shell=True, capture_output=True)
    server = server.stdout.decode("utf-8").strip()
    return f"{user}@{server}"


def monitor_gpu_utilization(
    check_interval: int = 900,  # seconds
    n_checks_pr_ping: int = 5,
    raise_alert_after_n_failed_checks: int = 2,  # n * check_interval
):
    """ """
    wandb.init(
        project="gpu-monitoring", entity="chcaa", mode="run", name="gpu-monitoring"
    )

    # check every
    n_failed_checks = 0
    while True:
        if gpu_is_used(n_checks_pr_ping):
            n_failed_checks = 0
            print("GPU is used")
        else:
            n_failed_checks += 1
            print("GPU is not used")
        if n_failed_checks >= raise_alert_after_n_failed_checks:
            not_used_time = n_failed_checks * check_interval
            human_readable_not_used_time = str(
                datetime.timedelta(seconds=not_used_time)
            )
            title = f"GPU has not been used for {human_readable_not_used_time}"
            text = (
                f"The GPU has not been used for {human_readable_not_used_time} (HH:MM:SS) on "
                + f"{get_server_name()}"
            )
            wandb.alert(
                title=title,
                text=text,
                level=AlertLevel.WARN,
            )
            print(f"Alert sent: {title} - {text}")
        time.sleep(check_interval)


def gpu_is_used(n_checks: int = 5):
    """
    A single check of whether the GPU utilization is non-zero.
    """
    for i in range(n_checks):
        utilization = get_gpu_utilization()
        if any([u > 0 for u in utilization]):
            return True
        time.sleep(0.3)
    return False


def get_gpu_utilization() -> List[float]:
    """
    A function to get GPU for all GPU utilization on using nvidia-smi

    Assumes it is run in bash shell
    """
    command = "nvidia-smi"
    output = subprocess.run(command, shell=True, capture_output=True)
    output = output.stdout
    # convert to string
    output = output.decode("utf-8")
    return get_gpu_utilization_from_nvidia_smi(output)


def get_gpu_utilization_from_nvidia_smi(output: str) -> List[float]:
    """

    Example:
        >>> nvida_smi_output = '''
        >>> +-----------------------------------------------------------------------------+
        >>> | NVIDIA-SMI 460.27.04    Driver Version: 460.27.04    CUDA Version: 11.2     |
        >>> |-------------------------------+----------------------+----------------------+
        >>> | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
        >>> | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
        >>> |                               |                      |               MIG M. |
        >>> |===============================+======================+======================|
        >>> |   0  Quadro RTX 8000     On   | 00000000:18:00.0 Off |                  Off |
        >>> | 34%   37C    P8    29W / 260W |      1MiB / 48601MiB |      0%      Default |
        >>> |                               |                      |                  N/A |
        >>> +-------------------------------+----------------------+----------------------+
        >>> |   1  Quadro RTX 8000     On   | 00000000:3B:00.0 Off |                    0 |
        >>> | 33%   44C    P2    70W / 260W |      1MiB / 45553MiB |      0%      Default |
        >>> |                               |                      |                  N/A |
        >>> +-------------------------------+----------------------+----------------------+
        >>> |   2  Quadro RTX 8000     On   | 00000000:86:00.0 Off |                  Off |
        >>> | 33%   46C    P0    77W / 260W |      1MiB / 48601MiB |      0%      Default |
        >>> |                               |                      |                  N/A |
        >>> +-------------------------------+----------------------+----------------------+
        >>> |   3  Quadro RTX 8000     On   | 00000000:AF:00.0 Off |                    0 |
        >>> | 33%   36C    P8    30W / 260W |      1MiB / 45553MiB |      0%      Default |
        >>> |                               |                      |                  N/A |
        >>> +-------------------------------+----------------------+----------------------+
        >>>
        >>> +-----------------------------------------------------------------------------+
        >>> | Processes:                                                                  |
        >>> |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
        >>> |        ID   ID                                                   Usage      |
        >>> |=============================================================================|
        >>> |  No running processes found                                                 |
        >>> +-----------------------------------------------------------------------------+
        >>> '''
        >>> get_gpu_utilization_from_nvidia_smi(nvida_smi_output)
        [0, 0, 0, 0]
    """  # noqa

    lines = output.split("\n")

    # extracts line ID for the GPUs 0-3 from the following line
    # |   0  Quadro RTX 8000     On   | 00000000:18:00.0 Off |                  Off |
    gpu_ids = [
        i
        for i, line in enumerate(lines)
        if line.startswith("|   ") and line[4].isdigit()
    ]
    gpu_utilization = []
    for gpu_id in gpu_ids:
        # extracts the GPU utilization from the following line
        # | 33%   36C    P8    30W / 260W |      1MiB / 45553MiB |      0%      Default
        gpu_utilization.append(float(lines[gpu_id + 1].split("|")[3].split("%")[0]))

    return gpu_utilization


if __name__ == "__main__":
    monitor_gpu_utilization()
