import sys
import os
import glob

# For local development: make osrm importable without installing the wheel.
# Symlinks the built osrm_ext*.so into src/osrm/ so the relative import works.
# In CI, cibuildwheel installs the wheel before running tests, so this is a no-op there.
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_pkg_dir = os.path.join(_root, "src", "osrm")
_build_dir = os.path.join(_root, "build")

for _so in glob.glob(os.path.join(_build_dir, "osrm_ext*.so")):
    _link = os.path.join(_pkg_dir, os.path.basename(_so))
    if not os.path.exists(_link):
        os.symlink(_so, _link)

sys.path.insert(0, os.path.join(_root, "src"))
