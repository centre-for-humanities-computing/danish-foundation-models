---
pretty_name: Folketinget (Danish Parliament)
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
# Dataset Card for Folketinget (Danish Parliament)
## Dataset Description
- **Number of records:** 1315
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'TALER 50: Mødet er åbnet. I dag er der følgende an',
    'source': 'dagw-ft',
    'id': 'ft_20121M100',
    'added': 'Sun Mar 28 09:58:44 2021 CEST +0200',
    'created': '2009-01-01T00:00:00.000Z, 2019-01-01T00:00:00.000Z',
    'metadata': {
        'domain': 'Conversation',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'Folketinget (Danish Parliament)'
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
