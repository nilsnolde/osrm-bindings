# py-osrm
![PUSH_CI](https://github.com/gis-ops/py-osrm/actions/workflows/push_master.yml/badge.svg)

**py-osrm is a Python package that binds to [osrm-backend](https://github.com/Project-OSRM/osrm-backend) using [nanobind](https://github.com/wjakob/nanobind).**

---

## Supported Platforms
Platform | Arch
---|---
Linux | x86_64
MacOS | x86_64
Windows | x86_64
---

## Installation
py-osrm is supported on **CPython 3.10+**, and can be installed from source via running the following command in the source folder:
```
pip install .
```

## OSRM Version

When building from source, the OSRM upstream version is controlled by `OSRM_GIT_TAG` in `pyproject.toml`:

```toml
[tool.scikit-build.cmake.define]
OSRM_GIT_TAG = "v6.0.0"
```

This accepts any git commit hash, branch name, or tag. To override it without editing the file, pass it as a config setting at install time:

```
pip install . --config-settings cmake.define.OSRM_GIT_TAG=<commit/tag/branch>
```

> [!NOTE]
> Update pyproject.toml regularly to build against newest OSRM release.

## Example
The following example will showcase the process of calculating routes between two coordinates.

First, import the `osrm` library, and instantiate an instance of OSRM:
```python
import osrm

# Instantiate py_osrm instance
py_osrm = osrm.OSRM("./tests/test_data/ch/monaco.osrm")
```

Then, declare `RouteParameters`, and then pass it into the `py_osrm` instance:
```python
# Declare Route Parameters
route_params = osrm.RouteParameters(
    coordinates = [(7.41337, 43.72956), (7.41546, 43.73077)]
)

# Pass it into the py_osrm instance
res = py_osrm.Route(route_params)

# Print out result output
print(res["waypoints"])
print(res["routes"])
```

---

## Documentation
[Documentation Page](https://gis-ops.github.io/py-osrm/)
