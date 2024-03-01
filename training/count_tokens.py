import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str, required=True)
parser.add_argument("--sample-size", type=int, default=8192)
args = parser.parse_args()

with open(args.path) as f:
    data = json.load(f)

shards = 0
samples = 0
for shard in data["shards"]:
    shards += 1
    samples += shard["samples"]

print(f"Shards: {shards:,}")
print(f"Samples: {samples:,}")

tokens = samples * args.sample_size
print(f"Tokens: {tokens:,}")


