from setuptools import setup
from setuptools import find_packages

import subprocess
import sys
import os

path = os.path.join("src", "dfm", "about.py")

with open(path) as f:
    v = f.read()
    for l in v.split("\n"):
        if l.startswith("__version__"):
            __version__ = l.split('"')[-2]


def install_nodeps(package_name: str):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--no-deps", package_name]
    )


def setup_package():
    # custom install of DaCy where we only install the requirements needed for the lookup tables:
    # should not be necessary after: https://github.com/centre-for-humanities-computing/DaCy/pull/98
    setup(
        version=__version__,
        packages=find_packages(
            "src",
            exclude=[
                "application",
            ],
        ),
        package_dir={"": "src"},
    )
    install_nodeps("dacy")


if __name__ == "__main__":
    setup_package()
