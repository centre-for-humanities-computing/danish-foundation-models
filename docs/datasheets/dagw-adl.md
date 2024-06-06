---
pretty_name:  Archive for Danish Literature
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
# Dataset Card for  Archive for Danish Literature
## Dataset Description
- **Number of records:** 498
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'SAMLEDE VÆRKER

JEPPE AAKJÆR GYLDENDALSKE BOGHANDE',
    'source': 'dagw-adl',
    'id': 'adl_aakjaer06val',
    'added': '2020-09-14',
    'created': '1700-01-01, 2022-01-01',
    'metadata': {
        'domain': 'Wiki & Books',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': ' Archive for Danish Literature'
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
<summary>Creative Commons Zero v1.0 Universal</summary>
<p>
Creative Commons Legal Code

CC0 1.0 Universal
</p>
</details>
