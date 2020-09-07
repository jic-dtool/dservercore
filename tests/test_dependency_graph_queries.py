"""Test the dependency graph querying."""

import json

from . import tmp_app_with_dependent_data
from . import compare_nested, compare_marked_nested, comparison_marker_from_obj
from . import TESTING_FAMILY, family_datasets

grumpy_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5NjJjODEyNi1kZDJlLTQ1NDEtODQyOC0yZDYxYjEwZmU0M2YiLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU1MzIyMzEzMywidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU1MzIyMzEzMywiaWRlbnRpdHkiOiJncnVtcHkifQ.K1YYcUp2jfpBhVd7ggBJ_mpnQT_ZAGRjfgrReoz9no6zZ_5Hlgq2YLUNFtFfr2PrqsaO5fKWUfKrR8bjMijtlRlAEmyCJvalqXDWvriMf2QowyR6IjKxSNZcVCMkJXEk7cRlEM9f815YABc3RsG1F75n2dV5NSuvcQ4dQoItvNYpsuHZ3c-xYQuaQt7_Ch50Ez-H2fJatXQYdnHruyZOJQKPIssxU_yyeCnlOGklCmDn8mIolQEChrvW9HhpvgXsaAWEHjtNRK4T_ZH37Dq44fIB9ax6GGRZHDjWmjOicrGolfu73BuI8fOpLLpW5af6SKP-UhZA4AcW_TYG4PnOpQ"  # NOQA

TESTING_FAMILY_DEPENDENCIES = [
    {'derived_from': [
        {'uuid': 'a2218059-5bd0-4690-b090-062faf08e042'},
        {'uuid': 'a2218059-5bd0-4690-b090-062faf08e043'}],
     'name': 'brother',
     'uuid': 'a2218059-5bd0-4690-b090-062faf08e044'},
    {'derived_from': [{'uuid': 'unknown'}],
     'name': 'ex-husband',
     'uuid': 'a2218059-5bd0-4690-b090-062faf08e047'},
    {'derived_from': [{'uuid': 'unknown'}],
     'name': 'father',
     'uuid': 'a2218059-5bd0-4690-b090-062faf08e043'},
    {'name': 'grandfather',
     'uuid': 'a2218059-5bd0-4690-b090-062faf08e040'},
    {'derived_from': [{'uuid': 'a2218059-5bd0-4690-b090-062faf08e039'}],
     'name': 'grandmother',
     'uuid': 'a2218059-5bd0-4690-b090-062faf08e041'},
    {'derived_from': [
        {'uuid': 'a2218059-5bd0-4690-b090-062faf08e040'},
        {'uuid': 'a2218059-5bd0-4690-b090-062faf08e041'}],
     'name': 'mother',
     'uuid': 'a2218059-5bd0-4690-b090-062faf08e042'},
    {'derived_from': [
        {'uuid': 'a2218059-5bd0-4690-b090-062faf08e042'},
        {'uuid': 'a2218059-5bd0-4690-b090-062faf08e043'}],
     'name': 'sister',
     'uuid': 'a2218059-5bd0-4690-b090-062faf08e045'},
    {'derived_from': [
        {'uuid': 'a2218059-5bd0-4690-b090-062faf08e042'},
        {'uuid': 'a2218059-5bd0-4690-b090-062faf08e047'}],
     'name': 'stepsister',
     'uuid': 'a2218059-5bd0-4690-b090-062faf08e046'},
]

def test_dependency_graph_custom_aggregation(tmp_app_with_dependent_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)

    match = {'$match': {'name': 'brother'}}

    graph_lookup = {
            '$graphLookup': {
              'from': 'dependencies',
              'startWith': '$uuid',
              'connectFromField': 'dependencies',
              'connectToField': 'uuid',
              'as': 'dependency_graph',
            }
        }

    unwind = {'$unwind': '$dependency_graph'}

    replace_root = {
            '$replaceRoot': {
                'newRoot': '$dependency_graph'
            }
        }

    lookup = {
            '$lookup': {
               'from': 'datasets',
               'localField': 'uuid',
               'foreignField': 'uuid',
               'as': 'dataset',
             }
        }

    unwind_again = {'$unwind': '$dataset'}

    replace_root_again = {
            '$replaceRoot': {
                'newRoot': '$dataset'
            }
        }

    project = {
            '$project': {
                '_id': False,
                'uuid': True,
                'name': True,
                'derived_from': '$readme.derived_from',
            }
        }

    sort = {
            '$sort': {'name': 1}
    }

    aggregation = [
        match,
        graph_lookup,
        unwind,
        replace_root,
        lookup,
        unwind_again,
        replace_root_again,
        project,
        sort,
    ]

    query = {
        'aggregation': aggregation
    }

    r = tmp_app_with_dependent_data.post(
        "/dataset/aggregate",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200

    expected_response = TESTING_FAMILY_DEPENDENCIES
    response = json.loads(r.data.decode("utf-8"))
    assert compare_nested(response, expected_response)


def test_query_dependency_graph(tmp_app_with_dependent_data):  # NOQA

    headers = dict(Authorization="Bearer " + grumpy_token)

    uuid = "a2218059-5bd0-4690-b090-062faf08e044"  # brother

    r = tmp_app_with_dependent_data.get(
        "/dataset/graph/{}".format(uuid),
        headers=headers,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode("utf-8"))

    expected_response = []
    for role, p in TESTING_FAMILY.items():
        if role == 'friend':
            continue  # skip unrelated family friend

        r = tmp_app_with_dependent_data.get(
            "/dataset/lookup/{}".format(p['uuid']),
            headers=headers,
        )
        assert r.status_code == 200
        ref_response = json.loads(r.data.decode("utf-8"))
        expected_response.extend(ref_response)

    expected_response = sorted(expected_response, key=lambda s: s['uuid'])

    marker = comparison_marker_from_obj(expected_response)
    # exclude fields not to compare
    for m in marker:
        m['created_at'] = False
        m['frozen_at'] = False

    assert compare_marked_nested(response, expected_response, marker)
