import os
from typing import Any, Dict

import yaml
from django.conf import settings
from django.db import transaction


def deep_update(base_dict: dict, update_with: dict) -> Dict[str, Dict]:
    """
    Method to replace dictionary values recursively, only updating keys present in the update_with dictionary.
    Args:
        base_dict (dict): The original dictionary to be updated.
        update_with (dict): The dictionary containing the updated values.

    Returns:
        dict: The updated base_dict.
    """
    for key, value in update_with.items():
        if isinstance(value, dict):
            base_dict_value = base_dict.get(key)

            if isinstance(base_dict_value, dict):
                deep_update(base_dict_value, value)
            else:
                base_dict[key] = value
        else:
            base_dict[key] = value
    return base_dict


def apply_on_commit(callable_) -> Any:
    if settings.USE_ON_COMMIT_HOOK:
        transaction.on_commit(callable_)
    else:
        callable_()


def yaml_coerce(value):
    """
    Coerce a value from a string representation using the yaml.safe_load method.

    This function is useful for converting string representations of various data types
    into their corresponding Python objects. It uses the yaml.safe_load method to parse
    the input string and return the resulting Python object.

    Parameters:
    - value (str or any): The value to be coerced. If the value is not a string, it will be returned as is.

    Returns:
    - any: The coerced value. If the input value was a string, it will be parsed using yaml.safe_load.
           Otherwise, the input value will be returned as is.
    """
    if isinstance(value, str):
        return yaml.load("dummy: " + value, Loader=yaml.SafeLoader)["dummy"]

    return value


def get_settings_from_environment(prefix):
    """
    This function retrieves environment variables starting with a given prefix,
    applies the yaml_coerce function to each value, and returns them as a dictionary.

    Parameters:
    - prefix (str): The prefix to match environment variable keys.

    Returns:
    - dict: A dictionary containing the coerced environment variables with keys starting with the given prefix.
    """
    prefix_len = len(prefix)
    return {key[prefix_len:]: yaml_coerce(value) for key, value in os.environ.items() if key.startswith(prefix)}
