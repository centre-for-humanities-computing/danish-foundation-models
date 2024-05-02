---
pretty_name: Wikipedia
language:
  - da
license: cc0-1.0
license_name: Creative Commons Zero v1.0 Universal
size_categories:
  - 100k-1M
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for Wikipedia
## Dataset Description
- **Number of records:** 264502
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Vimoutiers er en kommune i departementet Orne i Ba',
    'source': 'dagw-wiki',
    'id': 'wiki_366127',
    'added': 'Sun Mar 28 09:28:24 2021 CEST +0200',
    'created': '2019-01-01T00:00:00.000Z, 2021-01-01T00:00:00.000Z',
    'metadata': {
        'domain': 'Wiki & Books',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'Wikipedia'
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
