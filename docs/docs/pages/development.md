# Development Guide

## Installing for production

Pre-built wheels are published to PyPI for Linux (x86\_64), macOS (arm64), and Windows (amd64), requiring Python 3.12+:

```bash
pip install osrm-bindings
```

To build from source (e.g. unsupported platform, custom OSRM commit):

```bash
pip install osrm-bindings --no-binary osrm-bindings
```

Or from a local checkout:

```bash
pip install .
```

Source builds fetch and compile OSRM automatically — this takes a long time.
See [platform-specific notes](#platform-specific-build-requirements) for prerequisites.

## Installing for development

Clone the repo and install in editable mode with dev dependencies:

```bash
git clone https://github.com/nilsnolde/osrm-bindings
cd osrm-bindings
pip install -e ".[dev]"
```

Install pre-commit hooks:

```bash
pre-commit install
```

## Platform-specific build requirements

### Linux

No extra steps needed. Wheels are built inside a custom manylinux image
(`ghcr.io/nilsnolde/manylinux:2_28_osrm_python`) that has all OSRM
dependencies baked in. A regular source install will pull OSRM's dependencies
via the system package manager or build them from source.

### macOS

Install OSRM's C++ dependencies via Homebrew:

```bash
brew install lua tbb boost@1.90
brew link boost@1.90
```

### Windows

Windows uses [Conan](https://conan.io/) for OSRM's C++ dependencies. Install
it and generate a default profile before building:

```bash
pip install conan==2.27.0
conan profile detect --force
```

Pass `ENABLE_CONAN=ON` to CMake at build time (see below).

## Building locally

### Editable install (recommended for development)

A standard `pip install -e .` works, but by default pip uses PEP 517 isolated
builds — each invocation creates a temporary directory, compiles everything,
then discards it. This means OSRM is recompiled from scratch every time.

Use `--no-build-isolation` to make scikit-build-core reuse the persistent
build directory (`build/{wheel_tag}/`) across runs:

```bash
# Linux / macOS
pip install -e . --no-build-isolation

# Windows
pip install -e . --no-build-isolation -C cmake.define.ENABLE_CONAN=ON
```

The first run is slow (full OSRM compile). Subsequent runs only recompile
changed binding files.

!!! warning "Keep config flags identical across runs"
    scikit-build-core hashes its configuration to detect changes. If the flags
    differ between runs, it wipes the build directory and starts from scratch.

!!! warning "Generator mismatch"
    CMake records the generator in `CMakeCache.txt`. If you ever see
    `Does not match the generator used previously`, delete the build directory
    and rebuild from scratch:
    ```powershell
    Remove-Item -Recurse -Force build/cp312-abi3-win_amd64
    ```

### Building a wheel

After the editable install has compiled everything, produce a wheel without
recompiling:

```bash
# Linux / macOS
pip wheel . --no-build-isolation -w dist

# Windows
pip wheel . --no-build-isolation -C cmake.define.ENABLE_CONAN=ON -w dist
```

CMake finds the existing artifacts in the build directory and skips
recompilation. The wheel lands in `dist/`.

On Windows the wheel must be repaired with delvewheel to bundle the shared
Conan DLLs (tbb, hwloc — they can't be made fully static). The `conanrun.bat`
generated in the build tree already knows the exact Conan package paths, so
activating it before delvewheel is all that's needed:

```powershell
cmd /c "call build\cp312-abi3-win_amd64\_deps\libosrm-build\conanrun.bat && delvewheel repair dist\osrm_bindings-*.whl -w dist"
```

Inspect bundled shared libraries (Windows — run after `pip install delvewheel`):

```bash
delvewheel show dist/*.whl
```

### Compiler cache

On Linux and macOS, ccache is used automatically (pre-installed in the
manylinux image; installed via Homebrew for macOS CI).

On Windows, scikit-build-core defaults to the **Visual Studio generator**,
which does not support `CMAKE_CXX_COMPILER_LAUNCHER`. Neither ccache nor
sccache works out of the box — this matches CI behaviour (see the comment in
`push_master.yml`). The build dir reuse from `--no-build-isolation` is the
main speed optimisation for local Windows development; a compiler cache only
matters when OSRM itself needs recompiling.

### FetchContent and the patch step

OSRM is fetched via CMake FetchContent and patched with
`patches/conan-static-deps.patch`. When CMake re-configures (which happens on
every `pip install` or `pip wheel` invocation), FetchContent may re-run the
patch step. The `PATCH_COMMAND` uses `cmake/apply_patch.cmake`, which silently
skips the patch if it has already been applied, so re-configuring is always
safe.

## Running tests

Build the test data (requires the package to be installed so the `osrm`
executables are available):

```bash
# Linux / macOS
cd tests/data && make

# Windows
cd tests/data && windows-build-tests.bat
```

Load the shared memory datastore:

```bash
python -m osrm datastore tests/data/ch/monaco
```

Run the test suite:

```bash
pytest tests/
```

## Running cibuildwheel locally

[cibuildwheel](https://cibuildwheel.pypa.io/) builds wheels inside isolated
environments that closely match CI. Install it with:

```bash
pip install cibuildwheel
```

Build for the current platform:

```bash
cibuildwheel --platform linux    # requires Docker on non-Linux hosts
cibuildwheel --platform macos
cibuildwheel --platform windows
```

Wheels land in `wheelhouse/`.

**Windows note:** cibuildwheel's `config-settings` in pyproject.toml are
*replaced* (not merged) by `CIBW_CONFIG_SETTINGS_WINDOWS` if that env var is
set. Always include `ENABLE_CONAN=ON` explicitly when overriding via the env
var:

```bash
$env:CIBW_CONFIG_SETTINGS_WINDOWS = "cmake.define.ENABLE_CONAN=ON"
cibuildwheel --platform windows
```

**Linux note:** The manylinux container mounts the host ccache directory via a
Docker volume. Set `CCACHE_DIR` on the host so the mount path matches what CI
uses:

```bash
CIBW_CONTAINER_ENGINE="docker; create_args: --volume /tmp/ccache:/ccache" \
CIBW_ENVIRONMENT_LINUX="CCACHE_DIR=/ccache" \
cibuildwheel --platform linux
```

## Type stubs

`src/osrm/osrm_ext.pyi` is auto-generated by `nanobind_add_stub()` at build
time and committed to the repository so mkdocstrings can build docs without
compiling the extension. CI verifies it is up to date (`check_stubs` job in
`pull_request.yml`).

After changing C++ bindings, rebuild and commit the updated stub:

```bash
pip install -e . --no-build-isolation   # regenerates the .pyi
git add src/osrm/osrm_ext.pyi
```

To regenerate manually without a full rebuild:

```bash
pip install nanobind ruff
python -m nanobind.stubgen -m osrm.osrm_ext -o src/osrm/osrm_ext.pyi
ruff format src/osrm/osrm_ext.pyi
```

## Releasing

Releases are driven by git tags. `setuptools-scm` reads the tag to set the
package version — no manual version bumps needed.

1. Ensure `push_master.yml` is green on `main`.
2. Create and push an annotated tag:
   ```bash
   git tag -a v1.2.3 -m "v1.2.3"
   git push origin v1.2.3
   ```
3. The `publish_wheels.yml` workflow triggers on tag push. It builds wheels for
   Linux and macOS, then uploads to PyPI via trusted publisher (no API token
   needed).
4. Verify the release at [pypi.org/project/osrm-bindings](https://pypi.org/project/osrm-bindings/).

**Test release without tagging:** trigger `publish_wheels.yml` manually via
`workflow_dispatch` with the `upload` input set to `true`. This builds and
uploads to TestPyPI.

**Windows wheels:** the `publish_wheels.yml` matrix currently only includes
Linux and macOS (`TODO` in the workflow). To include Windows, add `windows` to
the matrix and ensure the Conan cache restore step runs for that platform.

**ccache restore key:** `publish_wheels.yml` hardcodes
`ccache-${{ runner.os }}-nn-update-osrm` as the restore key. Update this to
`ccache-${{ runner.os }}-main` (or whichever branch you develop on) before
releasing from a different branch.
