"""Validation utility functions."""

from datetime import datetime, timezone


def _naive_utc_from_timestamp(timestamp):
    """Return a naive UTC datetime for a Unix timestamp.

    Naive UTC datetimes are used throughout dservercore because
    dtoolcore.utils.timestamp() only accepts naive datetimes.
    """
    return datetime.fromtimestamp(
        float(timestamp), timezone.utc).replace(tzinfo=None)


def extract_created_at_as_datetime(admin_metadata):
    """Return created_at as datetime
    Use frozen_at if created_at is missing.
    Deal with some created_at values being strings.
    """
    try:
        created_at = admin_metadata["created_at"]
    except KeyError:
        created_at = admin_metadata["frozen_at"]
    return _naive_utc_from_timestamp(created_at)


def extract_frozen_at_as_datetime(admin_metadata):
    frozen_at = admin_metadata["frozen_at"]
    return _naive_utc_from_timestamp(frozen_at)
