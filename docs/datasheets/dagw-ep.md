---
pretty_name: European Parliament
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
# Dataset Card for European Parliament
## Dataset Description
- **Number of records:** 4213
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'TALER 6703: Jeg har stemt for henstillingen om god',
    'source': 'dagw-ep',
    'id': 'ep_07-02-01-008',
    'added': '2019-11-20',
    'created': '2004-01-01, 2009-01-01',
    'metadata': {
        'domain': 'Conversation',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'European Parliament'
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
