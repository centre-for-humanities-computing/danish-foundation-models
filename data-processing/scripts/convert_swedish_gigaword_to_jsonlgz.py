from datetime import datetime
import xml.etree.ElementTree as ET
import bz2
import gzip
import json
import os
from multiprocessing import Pool
from tqdm import tqdm
import glob
import logging
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def concatenate_text_elements(elem):
    """
    Concatenate text content of <w> elements, considering words and punctuation.
    Punctuation marks are appended directly to the preceding word.
    """
    text_parts = []
    # Track if the previous element was punctuation
    prev_was_punct = False

    for child in elem.iter():
        if child.tag == 'w':
            text = child.text if child.text is not None else ""
            # Assume punctuation if the text is not alphanumeric
            is_punct = not text.strip().isalnum()
            if is_punct:
                if text_parts and not prev_was_punct:
                    # Append punctuation to the previous word
                    text_parts[-1] += text
                else:
                    text_parts.append(text)
                prev_was_punct = True
            else:
                text_parts.append(text)
                prev_was_punct = False
        elif child.tag == 'sentence':
            text_parts.append('\n')
            prev_was_punct = False

    # Join with space, but this time punctuation is already correctly attached to words
    document_text = " ".join(text_parts).strip()
    return document_text

def find_xml_bz2_files(directories):
    """
    Find all .xml.bz2 files within given directories.
    """
    bz2_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".xml.bz2"):
                    bz2_files.append(os.path.join(root, file))
    return bz2_files

def process_file(bz2_file_path):
    """
    Process a single XML .bz2 file and return a list of JSON objects.
    """
    logging.info(f"Starting processing file: {bz2_file_path}")
    json_objects = []
    with bz2.open(bz2_file_path, 'rt', encoding='utf-8') as file:
        for event, elem in ET.iterparse(file, events=('end',)):
            if elem.tag == 'text':
                document_text = concatenate_text_elements(elem)
                # Just in case we got a None
                corpus_id =  str(uuid.uuid4()) if elem.get('id') is None else elem.get('id')

                year = elem.get('year')
                datefrom_raw = elem.get('datefrom') if elem.get('datefrom') else f"{year}0101"
                dateto_raw = elem.get('dateto') if elem.get('dateto') else f"{year}1231"
                datefrom = datetime.strptime(datefrom_raw, "%Y%m%d").strftime("%Y-%m-%dT%H:%M:%S.000Z")
                dateto = datetime.strptime(dateto_raw, "%Y%m%d").strftime("%Y-%m-%dT%H:%M:%S.000Z")
                created_range = f"{datefrom}, {dateto}"
                added_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

                json_obj = {
                    "id": corpus_id,
                    "text": document_text,
                    "source": "Swedish gigaword",
                    "added": added_timestamp,
                    "created": created_range,
                    "metadata": {
                        "year": year,
                        "genre": elem.get('genre'),
                        "librisid": elem.get('librisid')
                    }
                }

                json_objects.append(json_obj)
                elem.clear()
    logging.info(f"Finished processing file: {bz2_file_path}")
    return json_objects


def process_files_in_parallel(directories, output_file_path):
    """
    Process XML .bz2 files found in several directories in parallel,
    with a progress bar, and write their contents to a single .jsonl.gz file.
    """
    all_bz2_files = find_xml_bz2_files(directories)

    with Pool(processes=48) as pool:
        results = list(tqdm(pool.imap(process_file, all_bz2_files), total=len(all_bz2_files)))

    with gzip.open(output_file_path, 'wt', encoding='utf-8') as f:
        for json_objects in results:
            for obj in json_objects:
                f.write(json.dumps(obj, ensure_ascii=False) + '\n')
directories = ['/work/github/swedish_gigaword/gigaword/1950', '/work/github/swedish_gigaword/gigaword/1960', '/work/github/swedish_gigaword/gigaword/1970', '/work/github/swedish_gigaword/gigaword/1980', '/work/github/swedish_gigaword/gigaword/1990', '/work/github/swedish_gigaword/gigaword/2000', '/work/github/swedish_gigaword/gigaword/2010']
output_file_path = '/work/github/swedish_gigaword/gigaword/swedish_gigaword_new.jsonl.gz'
process_files_in_parallel(directories, output_file_path)