"""Validation utility functions."""

from datetime import datetime


def extract_created_at_as_datetime(admin_metadata):
    """Return created_at as datetime
    Use frozen_at if created_at is missing.
    Deal with some created_at values being strings.
    """
    try:
        created_at = admin_metadata["created_at"]
    except KeyError:
        created_at = admin_metadata["frozen_at"]
    created_at = float(created_at)
    return datetime.utcfromtimestamp(created_at)


def extract_frozen_at_as_datetime(admin_metadata):
    frozen_at = admin_metadata["frozen_at"]
    frozen_at = float(frozen_at)
    return datetime.utcfromtimestamp(frozen_at)
