pip install nbconvert

jupyter nbconvert --to markdown docs/tutorials/finetune.ipynb
jupyter nbconvert --to markdown docs/tutorials/merge.ipynb

# move to blog
mv docs/tutorials/finetune.md docs/blog/posts/finetune.md
mv docs/tutorials/merge.md docs/blog/posts/merge.md


# You will have to manually add the deliminator:
# 
# <!-- more -->