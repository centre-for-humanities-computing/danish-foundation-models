---
pretty_name: Synderjysk (Danish dialect)
language:
  - da
license: cc0-1.0
license_name: Creative Commons Zero v1.0 Universal
size_categories:
  - 1-10k
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for Synderjysk (Danish dialect)
## Dataset Description
- **Number of records:** 178
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Mangeægskage Hent printvenligt dokument her – Klik',
    'source': 'dagw-synne',
    'id': 'synne_forening_0140',
    'added': 'Fri Jun 26 10:36:35 2020 CEST +0200',
    'created': '2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z',
    'metadata': {
        'domain': 'Other',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'Synderjysk (Danish dialect)'
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
<summary>Creative Commons Zero v1.0 Universal</summary>
<p>
Creative Commons Legal Code

CC0 1.0 Universal
</p>
</details>
