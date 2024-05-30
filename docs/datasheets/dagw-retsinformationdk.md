---
pretty_name: retsinformation.dk (Danish legal information)
language:
  - da
license: other
license_name: Danish Copyright Law
size_categories:
  - 10k-100k
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for retsinformation.dk (Danish legal information)
## Dataset Description
- **Number of records:** 64043
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Den fulde tekst Pressenævnets kendelse i sag nr. 1',
    'source': 'dagw-retsinformationdk',
    'id': 'retsinformationdk_173889',
    'added': '2019-11-22',
    'created': '2000-01-01, 2022-01-01',
    'metadata': {
        'domain': 'Legal',
        'license': 'Danish Copyright law at https://www.retsinformation.dk/forms/r0710.aspx?id=164796 states 

 § 9. Love, administrative forskrifter, retsafgørelser og lignende offentlige aktstykker er ikke genstand for ophavsret.

Stk. 2. Bestemmelsen i stk. 1 gælder ikke for værker, der fremtræder som selvstændige bidrag i de i stk. 1 nævnte aktstykker. Sådanne værker må dog gengives i forbindelse med aktstykket. Retten til videre udnyttelse afhænger af de i øvrigt gældende regler.
',
        'source-pretty': 'retsinformation.dk (Danish legal information)'
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
<summary>Danish Copyright Law</summary>
<p>
Danish Copyright law at https://www.retsinformation.dk/forms/r0710.aspx?id=164796 states 

 § 9. Love, administrative forskrifter, retsafgørelser og lignende offentlige aktstykker er ikke genstand for ophavsret.

Stk. 2. Bestemmelsen i stk. 1 gælder ikke for værker, der fremtræder som selvstændige bidrag i de i stk. 1 nævnte aktstykker. Sådanne værker må dog gengives i forbindelse med aktstykket. Retten til videre udnyttelse afhænger af de i øvrigt gældende regler.

</p>
</details>
