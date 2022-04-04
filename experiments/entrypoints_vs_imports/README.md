# Basic example illustrating that entry points do not cause circular imports

## Setup

Install the two packages in development mode.

```
cd core && python setup.py develop && cd ..
cd plugin && python setup.py develop && cd ..
```

## Test

Run the test.

```
python test.py
```

Behold the output below, and the absence of circular import error messages.

```
core
plugin
```
