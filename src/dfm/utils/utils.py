import json


def read_json(file_path: str):
    """Function for reading a json file.

    Args:
        file_path (str): Path to a json file.

    Returns:
        d (dict): Dictionary with json content.
    """
    with open(file_path) as f:
        d = json.load(f)
    return d
