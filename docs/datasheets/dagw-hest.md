---
pretty_name: Hestenettet (Danish debate forum)
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
# Dataset Card for Hestenettet (Danish debate forum)
## Dataset Description
- **Number of records:** 14391
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Er den ikke kær? 
Jeg kan ikke forstå at der altid',
    'source': 'dagw-hest',
    'id': 'hest_forum112802271280227_0',
    'added': '2020-10-05',
    'created': '2000-01-01, 2022-01-01',
    'metadata': {
        'domain': 'Social Media',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'Hestenettet (Danish debate forum)'
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
