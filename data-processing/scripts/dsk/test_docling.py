import gzip
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import TableItem, TextItem
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from utils import create_JSONL, find_near_duplicates, remove_newlines

# previous `PipelineOptions` is now `PdfPipelineOptions`
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.do_cell_matching = False
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
# ...

## Custom options are now defined per format.
doc_converter = DocumentConverter(  # all of the below is optional, has internal defaults.
    allowed_formats=[
        InputFormat.PDF,
        InputFormat.MD,
        InputFormat.IMAGE,
        InputFormat.DOCX,
        InputFormat.HTML,
        InputFormat.PPTX,
        InputFormat.ASCIIDOC,
    ],  # whitelist formats, non-matching files are ignored.
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,  # pipeline options go here.
            backend=PyPdfiumDocumentBackend,  # optional: pick an alternative backend
        ),
        InputFormat.DOCX: WordFormatOption(
            pipeline_cls=SimplePipeline,  # default for office formats and HTML
        ),
    },
)


files = list(
    Path(
        "./data",
    ).glob("**/*.docx"),
)
results = doc_converter.convert_all(files)
out_file = gzip.open("test.jsonl.gz", mode="wb")
for result in results:
    file_path = result.input.file
    filename = result.input.file.name
    filetype = result.input.format.name
    filesize = result.input.filesize
    page_count = result.input.page_count

    metadata = {
        "filename": filename,
        "filetype": filetype,
        "filesize": filesize,
        "page_count": page_count,
        "file_path": str(file_path),
    }

    file_content = ""
    ## Iterate the elements in reading order, including hierachy level:
    for item, level in result.document.iterate_items():
        if isinstance(item, TextItem):
            if item.text == "":
                continue
            file_content += item.text
        elif isinstance(item, TableItem):
            table_df: pd.DataFrame = item.export_to_dataframe()
            dups = find_near_duplicates(table_df, 0.8)
            # Choose one column from each near-duplicate pair to keep
            columns_to_keep = table_df.columns.copy(deep=True)
            print(columns_to_keep, dups)
            for pair in dups:
                # Keep the first column in the pair, remove the second
                if pair[1] in columns_to_keep:
                    columns_to_keep = columns_to_keep.drop(pair[1])

            # Create a new DataFrame with the selected columns
            df_cleaned = table_df[list(columns_to_keep)]
            df_cleaned = remove_newlines(df_cleaned)
            file_content += df_cleaned.to_markdown(index=False, tablefmt="github")
        file_content += "\n\n"

    line = json.dumps(
        asdict(create_JSONL(file_content, "cBrain", metadata)),
        ensure_ascii=False,
    )

    out_file.write(f"{line}\n".encode())

out_file.close()
"""
text_paths = find_text_keys(document)
text_values = extract_text_values(document, list(text_paths))

print("\n\n".join(text_values))
"""
