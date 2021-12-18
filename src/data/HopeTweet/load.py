"""
A minimal example of how to load the dataset
"""
import os
f_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(f_path, ".."))

from datasets import load_dataset

dataset = load_dataset('HopeTweet', streaming=True)
train = dataset["train"]

print(train.info)

for i in train:
    print(i)
    break