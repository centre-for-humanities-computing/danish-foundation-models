import json
import yaml

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

def read_yaml(yaml_path):
    """Get a yaml object into a Python-dictionary.

    Args:
        yaml_path (str): Path to yaml object.

    Returns:
        dict: A dictionary.
    """
    with open(yaml_path) as yaml_file:
        yaml_object = yaml.load(yaml_file, Loader=yaml.FullLoader)

    return yaml_object