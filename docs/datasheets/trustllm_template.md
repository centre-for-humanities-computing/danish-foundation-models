---
# General Information
pretty_name: {title} # [REQUIRED] Concise and descriptive name of dataset, e.g. Wikipedia
author: {author} # [REQUIRED] Name of the individual or organization primarily responsible for creating the dataset
doi: {doi} # [REQUIRED] DOI or other unique identifier if applicable

# Access and Usage
license: {license}  # [REQUIRED] Example: apache-2.0 or any license identifier from https://spdx.org/licenses/, use 'other' if not in the list.
license_name: {license_name}  # If license = other (license not in https://spdx.org/licenses), specify an id for it here, like `my-license-1.0`.
license_link: {license_link}  # If license = other, specify "LICENSE" or "LICENSE.md" to link to a file of that name inside the repo, or a URL to a remote file or write the full license terms in the markdown section.
publication_date: {publication_date} # [OPTIONAL] When the dataset was made available. Use ISO time format.

# Regulatory compliance
pii: {pii} # [REQUIRED] Does the data contain personal identifiable information? yes/no/unknown
copyright: {copyright} # [REQUIRED] Does the data contain copyrighted material? yes/no/unknown

# Technical specification
format: {format} # [REQUIRED] The file format of the dataset, (e.g. csv, json).
language: # [REQUIRED] ISO639-1 (two letter codes) or ISO639-3 (three letter codes)
- {lang_0}  # Example: fr
- {lang_1}  # Example: en
version: # [REQUIRED] Version of the dataset to track updates and changes
size_categories: {size} # [RECOMMENDED] The size 
- {number_of_elements_in_dataset}  # Example: n<1K, 100K<n<1M, …

# Content specifics
tags: # A set of keywords or subjects describing the dataset's focus, which aids in searchability and categorization
- {tag_0}
- {tag_1}

modalities: # Set of data modalities (text, video, audio, tabular...)
- {modality_0} # Example: text
- {modality_1}

temporal_coverage: {time_period} # [OPTIONAL] Time period during which the data was collected e.g. 2000-2010

geographical_coverage: # [RECOMMENDED] Specifies the geographic area the data pertains to. While 'Global' can be used for datasets that span multiple regions without specific focus, providing more specific details is preferable if known. Examples include naming a continent( e.g., America, Asia, Europe), a country or set of countries (e.g., Italy, China, Morocco), depending on the scope and source of the data
- {area_0}
- {area_1}

# Provenance and lineage
source_datasets: # [REQUIRED] Origin of the data, if derived from other datasets or sources.
- {source_dataset_0}  # Example: wikipedia
- {source_dataset_1}  # Example: laion/laion-2b


---

# Dataset Card for {{pretty_name}}
A brief summary explaining the dataset's purpose, contents, and potential applications (max 256 characters)
{dataset_summary} (REQUIRED)



## Dataset Details

### Dataset description [REQUIRED]

<!-- Provide a longer summary of what this dataset is. -->

{{ dataset_description | default("", true) }}

- **Curated by:** {{ curators | default("[More Information Needed]", true)}}
- **Funded by [optional]:** {{ funded_by | default("[More Information Needed]", true)}}
- **Shared by [optional]:** {{ shared_by | default("[More Information Needed]", true)}}
- **Language(s) (NLP):** {{ language | default("[More Information Needed]", true)}}
- **License:** {{ license | default("[More Information Needed]", true)}}

### Dataset Sources [OPTIONAL]

<!-- Provide the basic links for the dataset. -->

- **Repository:** {{ repo | default("[More Information Needed]", true)}}
- **Paper [optional]:** {{ paper | default("[More Information Needed]", true)}}
- **Demo [optional]:** {{ demo | default("[More Information Needed]", true)}}

## Uses [RECOMMENDED]

<!-- Address questions around how the dataset is intended to be used. -->

### Direct Use

<!-- This section describes suitable use cases for the dataset. -->

{{ direct_use | default("[More Information Needed]", true)}}

### Out-of-Scope Use

<!-- This section addresses misuse, malicious use, and uses that the dataset will not work well for. -->

{{ out_of_scope_use | default("[More Information Needed]", true)}}

## Dataset Structure [OPTIONAL]

<!-- This section provides a description of the dataset fields, and additional information about the dataset structure such as criteria used to create the splits, relationships between data points, etc. -->

{{ dataset_structure | default("[More Information Needed]", true)}}


## Dataset Creation [RECOMMENDED]

### Curation Rationale

<!-- Motivation for the creation of this dataset. -->

{{ curation_rationale_section | default("[More Information Needed]", true)}}

### Source Data

<!-- This section describes the source data (e.g. news text and headlines, social media posts, translated sentences, ...). -->

#### Data Collection and Processing

<!-- This section describes the data collection and processing process such as data selection criteria, filtering and normalization methods, tools and libraries used, etc. -->

{{ data_collection_and_processing_section | default("[More Information Needed]", true)}}

#### Who are the source data producers?

<!-- This section describes the people or systems who originally created the data. It should also include self-reported demographic or identity information for the source data creators if this information is available. -->

{{ source_data_producers_section | default("[More Information Needed]", true)}}

### Annotations [optional]

<!-- If the dataset contains annotations which are not part of the initial data collection, use this section to describe them. -->

#### Annotation process

<!-- This section describes the annotation process such as annotation tools used in the process, the amount of data annotated, annotation guidelines provided to the annotators, interannotator statistics, annotation validation, etc. -->

{{ annotation_process_section | default("[More Information Needed]", true)}}

#### Who are the annotators?

<!-- This section describes the people or systems who created the annotations. -->

{{ who_are_annotators_section | default("[More Information Needed]", true)}}

#### Personal and Sensitive Information

<!-- State whether the dataset contains data that might be considered personal, sensitive, or private (e.g., data that reveals addresses, uniquely identifiable names or aliases, racial or ethnic origins, sexual orientations, religious beliefs, political opinions, financial or health data, etc.). If efforts were made to anonymize the data, describe the anonymization process. -->

{{ personal_and_sensitive_information | default("[More Information Needed]", true)}}

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

{{ bias_risks_limitations | default("[More Information Needed]", true)}}

### Recommendations

<!-- This section is meant to convey recommendations with respect to the bias, risk, and technical limitations. -->

{{ bias_recommendations | default("Users should be made aware of the risks, biases and limitations of the dataset. More information needed for further recommendations.", true)}}

## Citation [optional]

<!-- If there is a paper or blog post introducing the dataset, the APA and Bibtex information for that should go in this section. -->

**BibTeX:**

{{ citation_bibtex | default("[More Information Needed]", true)}}

**APA:**

{{ citation_apa | default("[More Information Needed]", true)}}

## Glossary [optional]

<!-- If relevant, include terms and calculations in this section that can help readers understand the dataset or dataset card. -->

{{ glossary | default("[More Information Needed]", true)}}

## More Information [optional]

{{ more_information | default("[More Information Needed]", true)}}

## Dataset Card Authors [optional]

{{ dataset_card_authors | default("[More Information Needed]", true)}}

## Dataset Card Contact

{{ dataset_card_contact | default("[More Information Needed]", true)}}
