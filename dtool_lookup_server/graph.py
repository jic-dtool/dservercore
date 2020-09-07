"""Aggregation pipelines for graph operations."""

from dtool_lookup_server.config import Config


# a regular expression to filter valid v4 UUIDs
UUID_v4_REGEX = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[4][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}'


# most of those 'functions' are pretty static and just wrapped in function
# definitions for convenience.
def unwind_dependencies():
    """Create parallel aggregation pipelines for unwinding all configured dependency keys."""

    parallel_aggregations = []
    for dep_key in Config.DEPENDENCY_KEYS:
        aggregation = []
        hierarchy = dep_key.split('.')

        for i in range(len(hierarchy)):
            aggregation.append(
                {
                    '$unwind': {
                        'path': '$' + '.'.join(hierarchy[0:(i+1)]),
                        'preserveNullAndEmptyArrays': True,
                    }
                }
            )

        aggregation.append(
            {
                '$project': {
                    '_id': False,
                    'uuid': True,
                    'derived_from': '$' + dep_key,
                }
            }
        )
        parallel_aggregations.append(aggregation)

    return parallel_aggregations


def merge_dependencies():
    """Aggregate (directed) dependency graph edges.

    All configured dependency keys are merged in a key-agnostic 'dependencies'
    field."""

    parallel_aggregations = unwind_dependencies()

    aggregation = [
        {
            '$facet': {
                'key{:d}'.format(i): a for i, a in enumerate(parallel_aggregations)
            }
        },
        {
            '$project': {
                'dependencies': {
                    '$concatArrays': ['$key{:d}'.format(i) for i in range(len(parallel_aggregations))]
                }
            }
        },
        {
            '$unwind': {
                'path': '$dependencies',
                'preserveNullAndEmptyArrays': True,
            }
        },
        {
            '$replaceRoot': {
                'newRoot': '$dependencies'
            }
        }
    ]

    return aggregation


def group_dependencies():
    """Aggregate per-node adjacency lists of outgoing links."""
    aggregation = [
        {
            '$group': {
                '_id': '$uuid',
                'dependencies': {'$push': '$derived_from'}
            }
        },
        {
            '$project': {
                '_id': False,
                'uuid': '$_id',
                'dependencies': True
            }
        },
    ]
    return aggregation


def group_inverse_dependencies():
    """Aggregate per-node adjacency lists of incoming links."""
    aggregation = [
        {
            '$group': {
                '_id': '$derived_from',
                'dependencies': {'$push': '$uuid'}
            }
        },
        {
            '$project': {
                '_id': False,
                'uuid': '$_id',
                'dependencies': True
            }
        },
    ]
    return aggregation


def build_undirected_adjecency_lists():
    """Aggregate undirected adjacency lists."""
    aggregation = [
        *merge_dependencies(),
        {
            '$facet': {
                'derived_from': group_dependencies(),
                'derivative': group_inverse_dependencies(),
            }
        },
        {
            '$project': {
                'dependencies': {
                    '$concatArrays': ['$derived_from', '$derivative']
                }
            }
        },
        {
            '$unwind': {
                'path': '$dependencies',
                'preserveNullAndEmptyArrays': True,
            }
        },
        {
            '$replaceRoot': {
                'newRoot': '$dependencies'
            }
        },
        {  # filter invalid UUIDs (not UUID v4)
            '$match': {
                'uuid': {
                    '$regex': UUID_v4_REGEX
                },
            }
        },
        {
            '$group': {
                '_id': '$uuid',
                'dependencies': {'$push': '$dependencies'},
            }
        },
        {
            '$project': {
                '_id': False,
                'uuid': '$_id',
                'dependencies': True,
            }
        },
        {
            '$unwind': {
                'path': '$dependencies',
                'preserveNullAndEmptyArrays': True,
            }
        },
        {
            '$unwind': {
                'path': '$dependencies',
                'preserveNullAndEmptyArrays': True,
            }
        },
        {
            '$group': {
                '_id': '$uuid',
                'dependencies': {'$push': '$dependencies'}
            }
        },
        {
            '$project': {
                '_id': True,
                'uuid': '$_id',
                'dependencies': True
            }
        },
    ]
    return aggregation


def query_dependency_graph(pre_query, post_query=None):
    """Aggregation pipeline for querying dependency view on datasets collection.

    pre_query selects all documents for whicht to query the dependency graph.
    post_query allows removing certain documents from the results."""

    pre_match = {'$match': pre_query}

    graph_lookup = {
        '$graphLookup': {
          'from': Config.MONGO_DEPENDENCY_VIEW,
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
           'from': Config.MONGO_COLLECTION,
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

    post_match = {}
    if post_query:
        post_match = {'$match': post_query}

    # The interesting part is done here.
    # Now follows some restructuring in order to always
    # output unidirectional dependencies in a single 'dreived_from' field,
    # independent on the actual dependency keys used.

    # For each configured dependency key, the pipeline splits, unwinds and
    # projects the key in a uniformely named field 'derived_from'
    parallel_aggregations = []
    for dep_key in Config.DEPENDENCY_KEYS:
        cur_aggregation = []
        hierarchy = dep_key.split('.')

        for i in range(len(hierarchy)):
            cur_aggregation.append(
                {
                    '$unwind': {
                        'path': '$' + '.'.join(hierarchy[0:(i+1)]),
                        'preserveNullAndEmptyArrays': True,
                    }
                }
            )

        cur_aggregation.append(
            {
                '$project': {
                    '_id': False,
                }
            })
        cur_aggregation.append(
            {
                '$addFields': {
                    'derived_from': '$' + dep_key,
                }
            })
        parallel_aggregations.append(cur_aggregation)

    facet = {
        '$facet': {
            **{'key{:d}'.format(i): a for i, a in enumerate(parallel_aggregations)}
        }
    }

    # eventually, flatten lists and kill all unwound redundancies
    post_facet = [{
            '$project': {
                'nested': {
                    '$concatArrays': ['$key{:d}'.format(i) for i in range(len(parallel_aggregations))]
                }
            }
        }, {
            '$unwind': {
                'path': '$nested',
                'preserveNullAndEmptyArrays': True,
            }
        }, {
            '$group': {
                '_id': '$nested.uuid',
                'derived_from': {'$push': '$nested.derived_from'},
                'nested': {'$mergeObjects': '$nested'}
            }
        }, {
            '$addFields': {
                'nested.uuid': '$_id',
                'nested.derived_from': '$derived_from'
            }
        }, {
            '$replaceRoot': {'newRoot': '$nested'}
        }]

    sort = {  # for deterministic behavior only
        '$sort': {'uuid': 1}
    }

    project = {  # exclusion of fields as in utils.search_datasets_per_user
        '$project': {
            "_id": False,
            "readme": False,
            "manifest": False,
            "annotations": False,
        }
    }

    aggregation = [
        pre_match,
        graph_lookup,
        unwind,
        replace_root,
        lookup,
        unwind_again,
        replace_root_again,
        post_match,
        facet,
        *post_facet,
        sort,
        project
    ]
    return aggregation
