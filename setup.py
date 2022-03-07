from setuptools import setup
from setuptools import find_packages
import os

path = os.path.join("src", "dfm", "about.py")

with open(path) as f:
    v = f.read()
    for l in v.split("\n"):
        if l.startswith("__version__"):
            __version__ = l.split('"')[-2]


def setup_package():
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


if __name__ == "__main__":
    setup_package()
