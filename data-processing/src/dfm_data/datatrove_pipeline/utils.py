from typing import Any, Union

def dolma_to_datatrove_adapter(data: dict[str, Union[str, dict[str, Any], list[Any]]], path: str, id_in_file: int | str) -> dict[str, Any]:
    """
    Data adapter to adapt input data from Dolma into the datatrove Document format

    Args:
        data: a dictionary with the "raw" representation of the data
        path: file path or source for this sample
        id_in_file: its id in this particular file or source

    Returns: a dictionary with text, id, media and metadata fields

    """
    source_dolma = data.pop("source")
    id_dolma = data.pop("id")
    assert isinstance(source_dolma, str)
    assert isinstance(id_dolma, str)

    new_id = source_dolma + "+++" + id_dolma
    return {
        "text": data.pop("text", ""),
        "id": new_id,
        "media": data.pop("media", []),
        "metadata": data.pop("metadata", {}) | data,  # remaining data goes into metadata
    }
