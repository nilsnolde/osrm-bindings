import os
import platform
import site
import subprocess
import sys
from pathlib import Path

IS_WIN = platform.system().lower() == "windows"

# delvewheel bundles shared DLLs (tbb12, hwloc) into osrm_bindings.libs/.
# Subprocess-launched executables can't benefit from the .pyd DLL path
# patching, so we pass PATH explicitly on Windows.
_LIBS_DIR = Path(__file__).parent.parent / "osrm_bindings.libs"

if len(sys.argv) < 2:
    print("Argument not provided")
    sys.exit(1)

searchpaths = site.getsitepackages()
if site.ENABLE_USER_SITE:
    searchpaths.append(site.getusersitepackages())

exec = ""

for path in searchpaths:
    currpath = path + "/bin/"
    if os.path.isfile(currpath + "osrm-datastore") or os.path.isfile(currpath + "osrm-datastore.exe"):
        exec = currpath
        break

if not exec:
    print("Python OSRM executables not found")
    sys.exit(1)

if sys.argv[1] == "components":
    exec += "osrm-components"

elif sys.argv[1] == "contract":
    exec += "osrm-contract"

elif sys.argv[1] == "customize":
    exec += "osrm-customize"

elif sys.argv[1] == "datastore":
    exec += "osrm-datastore"

elif sys.argv[1] == "extract":
    exec += "osrm-extract"

elif sys.argv[1] == "partition":
    exec += "osrm-partition"

elif sys.argv[1] == "routed":
    exec += "osrm-routed"

for i in range(2, len(sys.argv)):
    exec += " " + sys.argv[i]

env = None
if IS_WIN and _LIBS_DIR.is_dir():
    env = {**os.environ, "PATH": str(_LIBS_DIR) + os.pathsep + os.environ.get("PATH", "")}

# will stream any output to the shell
# shell=True is safe here and lets people use "~" in paths etc
proc = subprocess.run(exec, encoding="utf-8", shell=True, env=env)
sys.exit(proc.returncode)
