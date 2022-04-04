from pkg_resources import iter_entry_points

def is_valid(name):
    return True

def echo():
    print(__name__)

def echo_all():
    for ep in iter_entry_points("core.hook"):
        f = ep.load()
        f()
