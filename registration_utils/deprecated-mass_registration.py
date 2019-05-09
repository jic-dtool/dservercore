"""Helpers script to register all datasets in a base URI."""

import argparse
import json

from datetime import date, datetime

import dtoolcore
import yaml
from pymongo import MongoClient

# Placeholder until app becomes a package or some other solution
# to the fact that "app" directory is not in the python path.
import os
import sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..")
sys.path.insert(0, _ROOT)

from app.utils import register_dataset  # NOQA


CONFIG_PATH = None

client = MongoClient()

db = client["dtool_info"]
collection = db["datasets"]


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {} not serializable".format(type(obj)))


def register_all_datasets(base_uri):
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)
    StorageBroker = dtoolcore._get_storage_broker(base_uri, CONFIG_PATH)
    for uri in StorageBroker.list_dataset_uris(base_uri, CONFIG_PATH):
        try:
            dataset = dtoolcore.DataSet.from_uri(uri)
        except dtoolcore.DtoolCoreTypeError:
            pass
        dataset_info = dataset._admin_metadata
        dataset_info["uri"] = dataset.uri

        # Add the readme info.
        readme_info = yaml.load(dataset.get_readme_content())
        dataset_info["readme"] = readme_info

        # Clean up datetime.data.
        dataset_info_json_str = json.dumps(dataset_info, default=json_serial)
        dataset_info = json.loads(dataset_info_json_str)

        r = register_dataset(collection, dataset_info)
        print("Registered: {}".format(r))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_uri")
    args = parser.parse_args()
    register_all_datasets(args.base_uri)
