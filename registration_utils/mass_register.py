import argparse

import requests

from dtool_lookup_server.utils import (
    iter_datasets_in_base_uri,
    generate_dataset_info,
)


def register_all_datasets_in_base_uri(base_uri, token, lookup_server_url):
    """Register all datasets in a base URI."""
    register_url = "/".join([lookup_server_url, "dataset", "register"])
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }
    for dataset in iter_datasets_in_base_uri(base_uri):
        print(dataset.uri)
        dataset_info = generate_dataset_info(dataset, base_uri)
        response = requests.post(
            register_url,
            headers=headers,
            json=dataset_info
        )
        print(response.status_code, response.reason)


def register_all_datasets(uri_list_file, token, lookup_server_url):
    with open(uri_list_file) as fh:
        for line in fh:
            base_uri = line.strip()
            register_all_datasets_in_base_uri(
                base_uri,
                token,
                lookup_server_url
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_uris_file")
    parser.add_argument("token")
    parser.add_argument("lookup_server_url")
    args = parser.parse_args()
    register_all_datasets(
        args.base_uris_file,
        args.token,
        args.lookup_server_url
    )
