---
pretty_name: DanNet (Danish WordNet)
language:
  - da
license: DanNet 1.0 License
license_name: DanNet 1.0 License
size_categories:
  - 10k-100k
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for DanNet (Danish WordNet)
## Dataset Description
- **Number of records:** 49040
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    'text': 'Når fodboldholdet fra 1. division i Ikast spiller ',
    'source': 'dagw-dannet',
    'id': 'dannet_46506',
    'added': 'Thu Sep 24 20:08:09 2020 +0000',
    'created': '2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z',
    'metadata': {
        'domain': 'dannet',
        'license': 'Commercial Use of DanNet

DanNet may be used in commercial applications in accordance with the following
license agreement. An attorney representing the commercial interest should
review this DanNet license with respect to the intended use.

DanNet 1.0 License

DanNet Release 2.1

This software and database is being provided to you, the LICENSEE, by University
of Copenhagen and Society for Danish Language and Literature under the following
license. By obtaining, using and/or copying this software and database, you
agree that you have read, understood, and will comply with these terms and
conditions.

Permission to use, copy, modify and distribute this software and database and
its documentation for any purpose and without fee or royalty is hereby granted,
provided that you agree to comply with the following copyright notice and
statements, including the disclaimer, and that the same appear on ALL copies of
the software, database and documentation, including modifications that you make
for internal use or for distribution.

THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND UNIVERSITY OF COPENHAGEN and
SOCIETY FOR DANISH LANGUAGE AND LITERATURE MAKE NO REPRESENTATIONS OR
WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION,
UNIVERSITY OF COPENHAGEN AND SOCIETY FOR DANISH LANGUAGE AND LITERATURE MAKE NO
REPRESENTATIONS OR WARRANTIES OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR
PURPOSE OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL
NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS.

The names of University of Copenhagen and Society for Danish Language and
Literature may not be used in advertising or publicity pertaining to
distribution of the software and/or database. Title to copyright in this
software, database and any associated documentation shall at all times remain
with University of Copenhagen and Society for Danish Language and Literature and
LICENSEE agrees to preserve same.

DanNet 2.1 Copyright 2009-12 by University of Copenhagen and Society for Danish',
        'source-pretty': 'DanNet (Danish WordNet)'
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
<summary>DanNet 1.0 License</summary>
<p>
Commercial Use of DanNet

DanNet may be used in commercial applications in accordance with the following
license agreement. An attorney representing the commercial interest should
review this DanNet license with respect to the intended use.

DanNet 1.0 License

DanNet Release 2.1

This software and database is being provided to you, the LICENSEE, by University
of Copenhagen and Society for Danish Language and Literature under the following
license. By obtaining, using and/or copying this software and database, you
agree that you have read, understood, and will comply with these terms and
conditions.

Permission to use, copy, modify and distribute this software and database and
its documentation for any purpose and without fee or royalty is hereby granted,
provided that you agree to comply with the following copyright notice and
statements, including the disclaimer, and that the same appear on ALL copies of
the software, database and documentation, including modifications that you make
for internal use or for distribution.

THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND UNIVERSITY OF COPENHAGEN and
SOCIETY FOR DANISH LANGUAGE AND LITERATURE MAKE NO REPRESENTATIONS OR
WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION,
UNIVERSITY OF COPENHAGEN AND SOCIETY FOR DANISH LANGUAGE AND LITERATURE MAKE NO
REPRESENTATIONS OR WARRANTIES OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR
PURPOSE OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL
NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS.

The names of University of Copenhagen and Society for Danish Language and
Literature may not be used in advertising or publicity pertaining to
distribution of the software and/or database. Title to copyright in this
software, database and any associated documentation shall at all times remain
with University of Copenhagen and Society for Danish Language and Literature and
LICENSEE agrees to preserve same.

DanNet 2.1 Copyright 2009-12 by University of Copenhagen and Society for Danish
</p>
</details>
