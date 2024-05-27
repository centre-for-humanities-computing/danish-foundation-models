---
pretty_name:  Danish news 2.0
language:
  - da
license: other
license_name: agreement
size_categories:
  - 10M<n<100M
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for Danews2.0
## Dataset Description
- **Number of records:** 26254962
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'id': 'e2a069b9',
    'text': 'Slottet sænker vindebroen 2011-04-12T00:00:00Z NYB...', 'source': 'danews2.0',
    'added': '2024-05-16',
    'created': '2011-04-12, 2012-04-11',
    'metadata': {
        'sub-source': 'LokalAvisen Nyborg',
        'ArticleUrl': 'https://mediaresearchapi.infomedia.dk/api/v1/article?id=e2a069b9',
        'Captions': [' Også i år skal der foretages arkæologiske udgravninger ved Nyborg Slot. Her fortæller Østfyns Museers Lars Ewald ( i midten med hat) forrige sommer om fundet af " den hemmelige tunnel." ARKIVFOTO: JØRGEN HANSEN'], 'Authors': [''],
        'WordCount': 169,
        'PageIds': ['42'],
        'Section': {'Name': '', 'Id': '1'}
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
Agreement with individual newspapers
