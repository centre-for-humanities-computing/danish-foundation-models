---
pretty_name: Johannes V. Jensen (Danish poet)
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
# Dataset Card for Johannes V. Jensen (Danish poet)
## Dataset Description
- **Number of records:** 42
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'JØRGINE JØRGINE KØBENHAVN HAGE & CLAUSENS FORLAG (',
    'source': 'dagw-jvj',
    'id': 'jvj_Jørgine',
    'added': '2020-06-26',
    'created': '1873-01-01, 1951-01-01',
    'metadata': {
        'domain': 'Wiki & Books',
        'license': 'Attribution-ShareAlike 4.0 International',
        'source-pretty': 'Johannes V. Jensen (Danish poet)'
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

## License Information
<details>
<summary>Creative Commons Attribution Share Alike 4.0</summary>
<p>
Attribution-ShareAlike 4.0 International
</p>
</details>
