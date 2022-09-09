# Results from corpus tagging


Each user tagged 100 documents unless otherwise specified. Documents were split by newlines into text-blocks, block was rated.
Text-blocks longer than 1000 characters were split into multiple blocks of 1000 characters or less.

This tagging scheme is similar to
([Kreutzer et al., 2022](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00447/109285/Quality-at-a-Glance-An-Audit-of-Web-Crawled)).

Each block was put into one of the following categories:
Each user tagged 100 documents (unless otherwise specified). Each document were tagged

- `wrong_language`: Not Danish
- `skipped`: Unsure of category
- `correct_language`: Danish text where at least 80% of the text is reasonable.
- `not_language`: Text where less than 80% of the text is reasonable. Takes priority over `wrong_language`.


Additionally, each block was tagged for pornography (yes/no) and offensiveness (yes/no).

## Text proportions

----


**Kenneth** (Session: test)

- *Date: 2022-09-05*
- *Sentences tagged: 102*
- *Documents tagged: na*

Proportions:

- 69.16% of characters is `correct_language`
- 25.66% of characters is `not_language`
- 2.74% of characters is `skipped`
- 2.45% of characters is `wrong_language`
- 0.00% of characters is porn
- 0.00% of characters is offensive

**Kenneth** (Session: 1)

- *Date: 2022-09-06*
- *Sentences tagged: 292*
- *Documents tagged: 100*

Proportions:

- 68.03% of characters is `correct_language`
- 29.19% of characters is `not_language`
- 2.10% of characters is `skipped`
- 0.68% of characters is `wrong_language`
- 0.00% of characters is porn
- 1.38% of characters is offensive

**Lasse** (Session: 1)

- *Date: 2022-09-07*
- *Sentences tagged: 336*
- *Documents tagged: 100*

Proportions:

- 68.02% of characters is `correct_language`
- 30.97% of characters is `not_language`
- 1.01% of characters is `wrong_language`
- 0.26% of characters is porn
- 0.00% of characters is offensive

## Intercoder Reliability

----

**Kenneth** (Session: test) vs **Kenneth** - (Session: 1)

- Cohen's Kappa (all categories): 0.8242 (Overlap in sentences: 98)

- Cohen's Kappa (correct_language vs not correct_language): 0.9075 (Overlap in sentences: 98)

**Kenneth** (Session: test) vs **Lasse** - (Session: 1)

- Cohen's Kappa (all categories): 0.8140 (Overlap in sentences: 95)

- Cohen's Kappa (correct_language vs not correct_language): 0.8389 (Overlap in sentences: 95)

**Kenneth** (Session: 1) vs **Lasse** - (Session: 1)

- Cohen's Kappa (all categories): 0.6767 (Overlap in sentences: 245)

- Cohen's Kappa (correct_language vs not correct_language): 0.7259 (Overlap in sentences: 245)


Comparison with mC4

-----

*Note*: mC4 did have a high degree of repititious texts. Similarly it did when texts blocks where not language they were often something like:

```
2lineStart%22%3A%22%22%2C%22placeholder%22%3A1%2C%22extName%22%3A%22nowiki%22%7D"" class=""placeholder placeholder-ext"" contenteditable=""false"">]&#x200b;</span></a></sup>&#x200b;</span>, at en lurifaks som Jimmy page, bruger MIT navn til opfindelsen! SV<span data-rte-instance=""1524-12953202845f3523698f3f1"" data-rte-meta=""%7B%22type%22%3A%22ext%22%2C%22wikitext%22%3A%22%3Cref%3ESVIN%3C%5C%2Fref%3E%22%2C%22lineStart%22%3A%22%22%2C%22placeholder%22%3A1%2C%22extName%22%3A%22ref%22%7D"" class=""placeholder placeholder-ext"" contenteditable=""false""><sup data-rte-washtml=""1"" id=""cite_ref-2"" class=""reference"" data-rte-attribs=""
```

While non-language texts in NAT was often menu bars, contact information, or navigation.


**Kenneth** (Session: 1)

- *Date: 2022-09-06*
- *Sentences tagged: 325*
- *Documents tagged: 100*

Proportions:

- 62.47% of characters is `correct_language`
- 34.88% of characters is `not_language`
- 1.27% of characters is `skipped`
- 1.38% of characters is `wrong_language`
- 3.25% of characters is porn
- 0.00% of characters is offensive