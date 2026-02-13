""" A collection of miscellaneous tools used by the feature extractor
"""

from typing import Dict, Any


def unnest(inputs: Dict[str, Any], _prefix="") -> Dict[str, Any]:
    """ Convert nested dictionaries (with string keys) to a dot-notation flat 
    dictionary.

    Parameters
    ---------
    inputs: The dictionary to unnest. Must have all string keys
    _prefix : Used during recursion to build up a dot-notation prefix. Don't 
        argue this yourself!
    
    Returns
    -------
    a flattened dictionary

    """

    unnested = {}
    for key, value in inputs.items():
        if isinstance(key, str):
            if isinstance(value, dict):
                unnested.update(unnest(value, _prefix=f"{key}."))
            else:
                unnested[f"{_prefix}{key}"] = value
        else:
            raise ValueError(f"found non-string key: {key}")
    return unnested
