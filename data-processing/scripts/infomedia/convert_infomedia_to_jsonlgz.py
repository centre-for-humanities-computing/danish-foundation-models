'''
Converting infomedia dataset.

ndjson -> jsonl.gz:

{
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "foo",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp we acquired this data (time file was created), specified as YYYY-MM-DDTHH:MM:SS.TIMEZONE e.g 2021-04-13T12:52:46.000Z
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available), should be specified as a range; "YYYY-MM-DDTHH:MM:SS.TIMEZONE, YYYY-MM-DDTHH:MM:SS.TIMEZONE"
    "metadata": {            # OPTIONAL: source-specific metadata
										"sub-source": "...", # OPTIONAL: E.g. "newspaper_ocr"
										...
								}
}
'''

import os
import re
import json
import gzip
import uuid
import tempfile
from datetime import datetime, timedelta
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

def format_created_range(publish_date, delay_days=365):
    """Create a formatted string representing a time range starting from `publish_date`."""
    start_date = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")
    end_date = start_date + timedelta(days=delay_days)
    return f"{start_date.strftime('%Y-%m-%d')}, {end_date.strftime('%Y-%m-%d')}"

def remove_html_tags(text: str) -> str:
    """Remove HTML tags from a string."""
    html_tag_pattern = re.compile('<.*?>', flags=re.MULTILINE)
    clean_text = re.sub(html_tag_pattern, " ", text)
    return clean_text

def remove_whitespace(text: str) -> str:
    """remove excess whitespace from text fields"""
    pat_ws = re.compile(pattern=r"\s\s+", flags=re.MULTILINE)
    clean_text = re.sub(pat_ws, " ", text)
    return clean_text

def process_file(filepath):
    """Process a single file and write its processed contents to a temporary file."""
    # Note: writing to the same file for all workers might lead to some problem.
    articles = []
    # Unique id
    temp_filename = f"/work/github/utilities/temp_files/temp_{uuid.uuid4().hex}.json"
    try:
        if filepath.endswith('.ndjson') and os.path.getsize(filepath) > 0:
            with open(filepath, 'r', encoding='utf-8') as file, open(temp_filename, 'w', encoding='utf-8') as temp_file:
                for line in file:
                    original = json.loads(line)
                    added = datetime.now().strftime('%Y-%m-%d')
                    # Extract the fields
                    heading = original.get("Heading", "")
                    sub_heading = original.get("SubHeading", "")
                    paragraph = original.get("Paragraph", "")
                    body_text = original.get("BodyText", "")
                    publish_date = original.get("PublishDate", "")
                    
                    # Check if Paragraph is identical to SubHeading or if Paragraph is in BodyText
                    if paragraph == sub_heading or paragraph in body_text:
                        paragraph_to_include = ""
                    else:
                        paragraph_to_include = paragraph
                    
                    # Concatenate the required fields with double newline characters \n\n
                    text_parts = [heading, sub_heading if paragraph_to_include == "" else paragraph_to_include, publish_date, body_text]
                    # filter removes empty strings
                    text = "\n\n".join(filter(None, text_parts))
                    # Remove HTML tags
                    text = remove_html_tags(text)
                    # Remove excess whitespace
                    text = remove_whitespace(text)
                    
                    transformed = {
                            "id": original.get("ArticleId", ""),
                            "text": text,
                            "source": "danew2.0",  # Fixed source value
                            "added": added,
                            "created": format_created_range(original.get("PublishDate", "2000-01-01T00:00:00Z")),
                            "metadata": {
                                "sub-source": original.get("Source", ""),  # Moving original source to metadata
                            }
                        }
                        
                        # Add remaining metadata fields excluding specific ones already extracted
                    for key, value in original.items():
                        if key not in ["ArticleId", "BodyText", "Source", "PublishDate", "Heading", "SubHeading", "Lead", "Paragraph"]:
                            transformed["metadata"][key] = value
                    json.dump(transformed, temp_file)
                    # Line break
                    temp_file.write('\n')
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        os.remove(temp_filename)  # Remove temporary file if error occurs
        return None
    return temp_filename

def init_file_paths(directory, max_files=-1):
    """Initialize a list of file paths to process, optionally limiting the number."""
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            filepath = os.path.join(root, name)
            # Non-empty files
            if os.path.getsize(filepath) > 0:
                file_paths.append(filepath)
                # return if reachs to max_files
                if 0 <= max_files == len(file_paths):
                    break
        if 0 <= max_files == len(file_paths):
            break
    return file_paths

def merge_temp_files(temp_files, output_jsonl_gz):
    """Merge temporary files into a single .jsonl.gz file."""
    with gzip.open(output_jsonl_gz, 'wt', encoding='utf-8') as gz_file:
        for i, temp_file in enumerate(temp_files):
            if temp_file:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    # Just in case
                    content = f.read().rstrip('\n').rstrip(',')
                    gz_file.write(content)
                    gz_file.write('\n')

def main(directory, output_jsonl_gz):
    """Multiprocessing to convert ndjson then merge all the processed files."""
    file_paths = init_file_paths(directory)
    with Pool(cpu_count()) as pool:
        temp_files = list(tqdm(pool.imap(process_file, file_paths), total=len(file_paths)))
    # Filter out None values in case some files failed to process
    temp_files = [f for f in temp_files if f is not None]
    merge_temp_files(temp_files, output_jsonl_gz)
    # Clean up temporary files
    for temp_file in temp_files:
        os.remove(temp_file)

if __name__ == '__main__':
    directory = '/work/github/infomedia'
    output_jsonl_gz = '/work/dfm-data/pre-training/danews2.0/articles.jsonl.gz'
    main(directory, output_jsonl_gz)
