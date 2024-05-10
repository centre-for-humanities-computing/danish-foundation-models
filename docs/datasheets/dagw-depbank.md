---
pretty_name: Danish Dependency Treebank
language:
  - da
license: cc-by-sa-4.0
license_name: Creative Commons Attribution Share Alike 4.0
size_categories:
  - 1-10k
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for Danish Dependency Treebank
## Dataset Description
- **Number of records:** 536
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': '
H.L. Hansen var en usædvanmlig og frodig personli',
    'source': 'dagw-depbank',
    'id': 'depbank_0375',
    'added': 'NA',
    'created': '2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z',
    'metadata': {
        'domain': 'Other',
        'license': 'Attribution-ShareAlike 4.0 International',
        'source-pretty': 'Danish Dependency Treebank'
        }
}
```

## Data Fields

- **id**: source-specific identifier.
- **text**: textual content of the document.
- **source**: source of the data.
- **added**: timestamp ai2 acquired this data.
- **created**": timestamp when original document was created (best-guess if not available)
- **metadata**: source-specific metadata.

## Lisence Information
<details>
<summary>Creative Commons Attribution Share Alike 4.0</summary>
<p>
Attribution-ShareAlike 4.0 International
</p>
</details>
