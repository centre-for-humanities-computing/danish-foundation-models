---
pretty_name: Skat (Danish tax authority)
language:
  - da
license: cc0-1.0
license_name: Creative Commons Zero v1.0 Universal
size_categories:
  - 10k-100k
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for Skat (Danish tax authority)
## Dataset Description
- **Number of records:** 14716
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Andelsboligforeningers levering af brugsrettighede',
    'source': 'dagw-skat',
    'id': 'skat_SKM2010.712.SKAT',
    'added': 'Thu Oct  1 11:40:33 2020 CEST +0200',
    'created': '2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z',
    'metadata': {
        'domain': 'Legal',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'Skat (Danish tax authority)'
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
