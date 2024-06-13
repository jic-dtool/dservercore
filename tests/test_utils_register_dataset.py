"""Test the dservercore.utils.register_dataset helper function."""

import pytest


def test_register_dataset(tmp_app_client):   # NOQA
    from dservercore import ValidationError
    from dservercore.utils import (
        register_users,
        register_base_uri,
        register_permissions,
        register_dataset,
        get_admin_metadata_from_uri,
        get_readme_from_uri_by_user,
    )

    register_users([
        dict(username="grumpy"),
        dict(username="sleepy"),
    ])

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"],
    }
    register_permissions(base_uri, permissions)

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {
                "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                    "hash": "d89117c9da2cc34586e183017cb14851",
                    "relpath": "U00096.3.rev.1.bt2",
                    "size_in_bytes": 5741810,
                    "utc_timestamp": 1536832115.0
                }
            }
        },
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536236399.19497,
        "number_of_items": 9876,
        "size_in_bytes": 5741810,
        "annotations": {"software": "bowtie2"},
        "tags": ["rnaseq"],
    }

    register_dataset(dataset_info)

    expected_content = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536236399.19497,
        "number_of_items": 9876,
        "size_in_bytes": 5741810,
    }
    assert get_admin_metadata_from_uri(uri) == expected_content
    assert get_readme_from_uri_by_user("sleepy", uri) == dataset_info["readme"]

    with pytest.raises(ValidationError):
        register_dataset({"name": "not-all-required-metadata"})


def test_register_dataset_without_created_at(tmp_app_client):   # NOQA
    from dservercore import ValidationError
    from dservercore.utils import (
        register_users,
        register_base_uri,
        register_permissions,
        register_dataset,
        get_admin_metadata_from_uri,
        get_readme_from_uri_by_user,
    )

    register_users([
        dict(username="grumpy"),
        dict(username="sleepy"),
    ])

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"],
    }
    register_permissions(base_uri, permissions)

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {
                "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                    "hash": "d89117c9da2cc34586e183017cb14851",
                    "relpath": "U00096.3.rev.1.bt2",
                    "size_in_bytes": 5741810,
                    "utc_timestamp": 1536832115.0
                }
            }
        },
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "number_of_items": 1232,
        "size_in_bytes": 5741810,
        "annotations": {"software": "bowtie2"},
        "tags": ["rnaseq"],
    }

    register_dataset(dataset_info)

    # When missing, created_at will be set to frozen_at.
    expected_content = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536238185.881941,
        "number_of_items": 1232,
        "size_in_bytes": 5741810,
    }
    assert get_admin_metadata_from_uri(uri) == expected_content
    assert get_readme_from_uri_by_user("sleepy", uri) == dataset_info["readme"]

    with pytest.raises(ValidationError):
        register_dataset({"name": "not-all-required-metadata"})


def test_register_dataset_without_created_at_and_size_in_bytes(tmp_app_client):   # NOQA
    from dservercore import ValidationError
    from dservercore.utils import (
        register_users,
        register_base_uri,
        register_permissions,
        register_dataset,
        get_admin_metadata_from_uri,
        get_readme_from_uri_by_user,
    )

    register_users([
        dict(username="grumpy"),
        dict(username="sleepy"),
    ])

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"],
    }
    register_permissions(base_uri, permissions)

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {
                "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                    "hash": "d89117c9da2cc34586e183017cb14851",
                    "relpath": "U00096.3.rev.1.bt2",
                    "size_in_bytes": 5741810,
                    "utc_timestamp": 1536832115.0
                }
            }
        },
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "annotations": {"software": "bowtie2"},
        "tags": ["rnaseq"],
    }

    register_dataset(dataset_info)

    # When missing, created_at will be set to frozen_at.
    expected_content = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536238185.881941,
        "number_of_items": None,
        "size_in_bytes": None,
    }
    assert get_admin_metadata_from_uri(uri) == expected_content
    assert get_readme_from_uri_by_user("sleepy", uri) == dataset_info["readme"]

    with pytest.raises(ValidationError):
        register_dataset({"name": "not-all-required-metadata"})


def test_register_too_large_metadata_dataset(tmp_app_client):  # NOQA

    from dservercore import ValidationError
    from dservercore.utils import (
        register_users,
        register_base_uri,
        register_permissions,
        register_dataset,
        get_admin_metadata_from_uri,
    )

    register_users([
        dict(username="grumpy"),
        dict(username="sleepy"),
    ])

    base_uri = "s3://snow-white"
    register_base_uri(base_uri)

    permissions = {
        "base_uri": base_uri,
        "users_with_search_permissions": ["grumpy", "sleepy"],
        "users_with_register_permissions": ["grumpy"],
    }
    register_permissions(base_uri, permissions)

    uuid = "af6727bf-29c7-43dd-b42f-a5d7ede28337"
    uri = "{}/{}".format(base_uri, uuid)
    dataset_info = {
        "base_uri": base_uri,
        "uuid": uuid,
        "uri": uri,
        "name": "my-dataset",
        "type": "dataset",
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {
                "e4cc3a7dc281c3d89ed4553293c4b4b110dc9bf3": {
                    "hash": "d89117c9da2cc34586e183017cb14851",
                    "relpath": "U00096.3.rev.1.bt2",
                    "size_in_bytes": 5741810,
                    "utc_timestamp": 1536832115.0
                }
            }
        },
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
        "created_at": 1536236399.19497,
        "annotations": {"software": "bowtie2"},
        "tags": ["rnaseq"],
    }

    really_large_readme = {}
    for i in range(100000):
        key = "here_is_a_long_key_{}".format(i)
        value = "here_is_a_long_value_{}".format(i) * 10
        really_large_readme[key] = value

    dataset_info["readme"] = really_large_readme

    # The dataset_info is too large and raises:
    # pymongo.errors.DocumentTooLarge: BSON document too large (28978543 bytes)
    # - the connected server supports BSON document sizes up to 16793598 bytes.
    # See https://github.com/jic-dtool/dservercore/issues/16
    # So the code catches this and raises dservercore.ValidationError
    # instead.
    with pytest.raises(ValidationError):
        register_dataset(dataset_info)

    assert get_admin_metadata_from_uri(dataset_info["uri"]) is None
