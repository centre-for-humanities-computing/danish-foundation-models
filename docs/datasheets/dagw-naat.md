---
pretty_name: NAAT
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
# Dataset Card for NAAT
## Dataset Description
- **Number of records:** 129
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Naar jeg i aften sender min nytaarshilsen til det ',
    'source': 'dagw-naat',
    'id': 'naat_1958kongfrederikix',
    'added': '2020-02-11',
    'created': '1930-01-01, 2022-01-01',
    'metadata': {
        'domain': 'Conversation',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'NAAT'
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
