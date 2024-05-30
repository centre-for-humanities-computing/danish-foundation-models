---
pretty_name:  nordjylland_news
language:
  - da
license: cc0-1.0
license_name: Creative Commons Zero v1.0 Universal
size_categories:
  - 10K<n<100K
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for nordjylland_news
## Dataset Description
- **Number of records:** 75219
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{
    "id": "nordjylland-news0",
    "text": "Opdatering: Manden er nu fundet af Nordjyllands Po...",
    "source": "nordjylland_news",
    "added": "2024-05-23",
    "created": "2024-05-23, 2025-05-23",
    "metadata": {
        "summary": "Nye oplysninger i sagen om en forsvunden mand har endnu en gang f\u00e5et politiet til at henvende sig til borgerne.",
        "text_len": 1739,
        "summary_len": 111,
        "sub-source": "TV2 Nord"
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
<summary>Creative Commons Zero v1.0 Universal</summary>
<p>
Creative Commons Legal Code

CC0 1.0 Universal
</p>
</details>
