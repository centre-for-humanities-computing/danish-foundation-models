---
pretty_name: Wikisource
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
# Dataset Card for Wikisource
## Dataset Description
- **Number of records:** 2429
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': '&lt;poem&gt;
Kæmpehøjen.
Jeg har stået på mindets ',
    'source': 'dagw-wikisource',
    'id': 'wikisource_4804',
    'added': '2021-03-28',
    'created': '1700-01-01, 2022-01-01',
    'metadata': {
        'domain': 'Wiki & Books',
        'license': 'Creative Commons Legal Code

CC0 1.0 Universal',
        'source-pretty': 'Wikisource'
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
