from importlib import metadata

def get_plugin(entrypoint_name):
    eps = metadata.entry_points(group=entrypoint_name)
    if len(eps) == 0:
        raise(RuntimeError(f"No entrypoint with name: {entrypoint_name}"))
    if len(eps) > 1:
        raise(RuntimeError(f"More than one entrypoints with name {entrypoint_name}"))
    return tuple(eps)[0].load()

auth_plugin = get_plugin("dtool_lookup_server.auth")