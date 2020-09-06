"""Aggregation pipelines for graph operations."""

from dtool_lookup_server.config import Config

# a regular expression to filter valid v4 UUIDs
UUID_v4_REGEX = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[4][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}'


# most of those 'functions' are pretty static and just wrapped in function
# definitions for convenience.
def unwind_dependencies():
    """Aggregate (directed) dependency graph edges."""
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
        *unwind_dependencies(),
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
