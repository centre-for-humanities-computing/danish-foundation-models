---
pretty_name: Bornholmsk (Danish dialect)
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
# Dataset Card for Bornholmsk (Danish dialect)
## Dataset Description
- **Number of records:** 106
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Ræua-Lârs

Ræua-Lârs å hans Konna, Stina, bode uda',
    'source': 'dagw-botxt',
    'id': 'botxt_0000040',
    'added': 'NA',
    'created': '2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z',
    'metadata': {
        'domain': 'Other',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'Bornholmsk (Danish dialect)'
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
