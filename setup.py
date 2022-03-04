from setuptools import setup
from setuptools import find_packages
import os


def setup_package():
    setup(
        packages=find_packages(
            "src",
            exclude=[
                os.path.join("src", "application"),
                os.path.join("src", "application", "*"),
            ],
        ),
        package_dir={"": "src"},
    )


if __name__ == "__main__":
    setup_package()
