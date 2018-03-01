"""Utility functions."""

def dataset_info_is_valid(dataset_info):
    """Return True if the dataset info is valid."""
    if "uuid" not in dataset_info:
        return False
    if "type" not in dataset_info:
        return False
    if "uri" not in dataset_info:
        return False
    return True
