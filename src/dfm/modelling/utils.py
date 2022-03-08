import yaml


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
