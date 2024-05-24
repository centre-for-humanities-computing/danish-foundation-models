---
pretty_name:  MeMo
language:
  - da
license: cc-by-4.0
license_name: Creative Commons Attribution 4.0 International
size_categories:
  - n<1K
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for memo
## Dataset Description
- **Number of records:** 858
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'id': '130024227090',
    'text': 'I . \nI den fornemste gade lå en prægtig , \ngammeld...',
    'source': 'memo',
    'added': '2024-05-16',
    'created': '1870-01-01, 1970-01-01',
    'metadata': {
        'file_received': 'y',
        'filename': '1870_AndersenHC_LykkePeer.pdf',
        'firstname': 'H.C.',
        'surname': 'Andersen',
        'pseudonym': None,
        'gender': 'm',
        'nationality': 'dk',
        'title': 'Lykke-Peer',
        'subtitle': None,
        'volume': None,
        'year': 1870,
        'pages': '183',
        'illustrations': 'n',
        'typeface': 'gothic',
        'publisher': 'Reitzel',
        'price': '2,25',
        'file_status': 'Modtaget fra KB 7.4.2022 DEL2 sending 5', 'notes': "OBS! PDF'en er ren tekst i antikva, men den fysiske bog formentlig fraktur. Det kalder på separate kolonner: pdf-typeface eller file-typeface og book-typeface. /PD",
        'filepath': None,
        'fileformat': 'pdftxt',
        'txt_received': 'y',
        'readable': 'y',
        'historical': 'n',
        'period': None,
        'period_notes': None,
        'novel_start': '10',
        'novel_end': '190',
        'novelstart_rescan': None,
        'novelend_rescan': None,
        'start_end_page_notes': None,
        'serialno': 12.0,
        'quarantine': None,
        'discard': None,
        'sub-source': 'KB'
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
