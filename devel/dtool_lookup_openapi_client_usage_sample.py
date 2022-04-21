import os
import time
import dtool_lookup_openapi_client
from pprint import pprint
from dtool_lookup_openapi_client.api import dataset_api
# from dtool_lookup_openapi_client.model.base_uri import BaseURI
from dtool_lookup_openapi_client.model.dataset_sql_alchemy import DatasetSQLAlchemy as Dataset
from dtool_lookup_openapi_client.model.error import Error
from dtool_lookup_openapi_client.model.pagination_metadata import PaginationMetadata
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

token = os.environ["TOKEN"]

# Configure Bearer authorization (JWT): bearerAuth
configuration = dtool_lookup_openapi_client.Configuration(host="http://localhost:5000", access_token=token)


# Enter a context with an instance of the API client
with dtool_lookup_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = dataset_api.DatasetApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    page_size = 10 # int |  (optional) (default to 10)

    try:
        # List all base_uris.
        api_response = api_instance.dataset_list_get(page=page, page_size=page_size)
        pprint(api_response)
    except dtool_lookup_openapi_client.ApiException as e:
        print("Exception when calling BaseUriApi->admin_base_uri_list_get: %s\n" % e)
