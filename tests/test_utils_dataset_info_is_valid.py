"""Test dservercore.utils.dataset_info_is_valid helper function."""

# Minimum data required to register a dataset.
INFO = {
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
    "annotations": {"stars": 5},
    "tags": ["empty", "dataset"],
}


def test_dataset_info_is_valid_returns_true_on_valid_info():
    from dservercore.utils import dataset_info_is_valid

    info = INFO.copy()
    assert dataset_info_is_valid(info)


def test_dataset_info_returns_false_when_key_data_is_missing():
    from dservercore.utils import dataset_info_is_valid

    for key in INFO.keys():

        info = INFO.copy()
        del info[key]
        assert not dataset_info_is_valid(info), key


def test_dataset_info_returns_false_when_type_is_not_dataset():
    from dservercore.utils import dataset_info_is_valid

    info = INFO.copy()
    info["type"] = "protodataset"
    assert not dataset_info_is_valid(info)


# TODO: This test should be deprecated by using marshmallow.UUID
def test_dataset_info_returns_false_if_uuid_looks_invalid():
    from dservercore.utils import dataset_info_is_valid

    info = INFO.copy()
    info["uuid"] = "af6727bf-29c7-43dd-b42f"
    assert not dataset_info_is_valid(info)


def test_dataset_info_is_valid_returns_false_if_base_uri_ends_with_slash():
    from dservercore.utils import dataset_info_is_valid

    info = INFO.copy()
    info["base_uri"] = "file:///tmp/"
    assert not dataset_info_is_valid(info)
