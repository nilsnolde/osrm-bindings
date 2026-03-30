# py-osrm
![PUSH_CI](https://github.com/gis-ops/py-osrm/actions/workflows/push_master.yml/badge.svg)

**py-osrm is a Python package that binds to [osrm-backend](https://github.com/Project-OSRM/osrm-backend) using [nanobind](https://github.com/wjakob/nanobind).**

---

## PyPI Supported Platforms

Platform | Arch
---|---
Linux | x86_64
MacOS | x86_64
Windows | x86_64
---

On PyPI we only distribute `abi3` wheels for each platform, i.e. one needs at least Python 3.12 to install the wheels. Of course it'll fall back to attempt an installation from source.

## Installation

py-osrm is (likely, didn't check) supported from **CPython 3.10+** on, and can be installed from source via running the following command in the source folder:

```
pip install .
```

## OSRM Version

When building from source, the OSRM upstream version is controlled by `OSRM_GIT_REPO` & `OSRM_GIT_TAG` in `pyproject.toml`:

```toml
[tool.scikit-build.cmake.define]
OSRM_GIT_REPO = "https://github.com/nilsnolde/osrm-backend"
OSRM_GIT_TAG = "de8a9da93aa09a4943d3964f0fb378a01a66af49"
```

This accepts any git commit hash, branch name, or tag. To override it without editing the file, pass it as a config setting at install time:

```
pip install . --config-settings cmake.define.OSRM_GIT_TAG=<commit/tag/branch>
```

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

## Type Stubs

The file `src/osrm/osrm_ext.pyi` contains auto-generated type stubs for the C++ extension module. These are used by IDEs for autocompletion and by mkdocstrings to build documentation without compiling the extension.

After changing C++ bindings, rebuild the project to regenerate the stubs:

```
pip install -e .
```

Then commit the updated `.pyi` file. CI will verify that committed stubs are up to date.

## Documentation
[Documentation Page](https://gis-ops.github.io/py-osrm/)
