# Data-processing Dansk Sprogmodel Konsortium (DSK)

This directory contains a script for processing the DSK data. It focuses mainly on converting from various formats (e.g. pdf and docx) to jsonl.

The script have an external dependency on `antiword` which should be installed separately. You do so on linux by running:

```bash
$ sudo apt-get install antiword
```

**NOTE:** `anitword` is only used for extracting text from `.doc` files, so if you don't need that you can skip that install.

Run the conversion on an entire directory:

```bash
$ python convert_dsk_to_jsonl.py $PATH_TO_DSK_DIR $OUTPUT_PATH $DSK_CLIENT
```

