"""Test dtool_lookup_server.utils.dataset_info_is_valid helper function."""


def test_dataset_info_is_valid_returns_true_on_valid_info():
    from dtool_lookup_server.utils import dataset_info_is_valid

    # Below is the minimum data required to register a dataset.
    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert dataset_info_is_valid(info)


def test_dataset_info_returns_false_when_key_data_is_missing():
    from dtool_lookup_server.utils import dataset_info_is_valid

    info = {
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)

    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)

    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)

    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)

    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "name": "my-dataset",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)

    info = {
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)

    # No creator_username.
    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)

    # No frozen_at.
    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
    }
    assert not dataset_info_is_valid(info)

    # No manifest.
    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)


def test_dataset_info_returns_false_when_type_is_not_dataset():
    from dtool_lookup_server.utils import dataset_info_is_valid

    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "protodataset",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)


def test_dataset_info_returns_false_if_uuid_looks_invalid():
    from dtool_lookup_server.utils import dataset_info_is_valid

    info = {
        "uuid": "af6727bf-29c7-43dd-b42f",
        "type": "protodataset",
        "uri": "file:///tmp/a_dataset",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "base_uri": "file:///tmp",
        "creator_username": "olssont",
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)


def test_dataset_info_is_valid_returns_false_if_base_uri_ends_with_slash():
    from dtool_lookup_server.utils import dataset_info_is_valid

    info = {
        "uuid": "af6727bf-29c7-43dd-b42f-a5d7ede28337",
        "type": "dataset",
        "uri": "file:///tmp/a_dataset",
        "base_uri": "file:///tmp/",
        "creator_username": "olssont",
        "name": "my-dataset",
        "readme": {"description": "test dataset"},
        "manifest": {
            "dtoolcore_version": "3.7.0",
            "hash_function": "md5sum_hexdigest",
            "items": {}
        },
        "frozen_at": 1536238185.881941,
    }
    assert not dataset_info_is_valid(info)
