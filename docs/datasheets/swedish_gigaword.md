---
pretty_name:  Swedish Gigaword
language:
  - sv
license: cc-by-4.0
license_name: Creative Commons Attribution 4.0 International
size_categories:
  - 10M<n<100M
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for swedish_gigaword
## Dataset Description
- **Number of records:** 50185534
- **Languages:** Swedish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'id': '1950:10',
    'text': 'National Librar of Sweden Denna bok digitaliserade...', 'source': 'swedish_gigaword',
    'added': '2024-05-23',
    'created': '1950-01-01, 1950-12-31',
    'metadata': {
        'year': '1950',
        'genre': 'government',
        'librisid': '13537973'
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
<summary>Creative Commons Attribution 4.0 International</summary>
<p>
Creative Commons Corporation ("Creative Commons") is not a law firm and does not provide legal services or legal advice. Distribution of Creative Commons public licenses does not create a lawyer-client or other relationship. Creative Commons makes its licenses and related information available on an "as-is" basis. Creative Commons gives no warranties regarding its licenses, any material licensed under their terms and conditions, or any related information. Creative Commons disclaims all liability for damages resulting from their use to the fullest extent possible.

https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/cc-by-4.0.md
</p>
</details>
