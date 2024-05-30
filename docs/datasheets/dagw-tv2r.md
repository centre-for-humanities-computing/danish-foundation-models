---
pretty_name: TV 2 Radio (Danish news)
language:
  - da
license: cc-by-sa-4.0
license_name: Creative Commons Attribution Share Alike 4.0
size_categories:
  - 10k-100k
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for TV 2 Radio (Danish news)
## Dataset Description
- **Number of records:** 49137
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Storken er landet
02 april 2017 kl. 17.58
Søndag a',
    'source': 'dagw-tv2r',
    'id': 'tv2r_92548',
    'added': '2019-11-13',
    'created': '2015-01-01, 2020-01-01',
    'metadata': {
        'domain': 'News',
        'license': 'The owner of this content is TV2 Regionerne, Denmark.
Creative Commons Attribution 4.0 International',
        'source-pretty': 'TV 2 Radio (Danish news)'
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
<summary>Creative Commons Attribution Share Alike 4.0</summary>
<p>
The owner of this content is TV2 Regionerne, Denmark.
Creative Commons Attribution 4.0 International
</p>
</details>
