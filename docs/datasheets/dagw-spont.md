---
pretty_name: Spontaneous speech
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
# Dataset Card for Spontaneous speech
## Dataset Description
- **Number of records:** 411
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Taler 6: mm
Taler 7: er du klar?
Taler 6: ja
Taler',
    'source': 'dagw-spont',
    'id': 'spont_PuzzleOfDanish132',
    'added': '2020-01-21',
    'created': '2019-01-01, 2020-01-01',
    'metadata': {
        'domain': 'Conversation',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'Spontaneous speech'
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
