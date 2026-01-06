import sys
import os
import platform


addon_path = os.path.dirname(__file__)
libs_path = os.path.join(addon_path, "libs")
target_lib = None

system = platform.system()
machine = platform.machine()

if system == "Windows":
    if machine.endswith("64"):
        target_lib = "win64"
    
elif system == "Linux":
    target_lib = "linux" 

elif system == "Darwin": 
    if "arm" in machine or "aarch64" in machine:
        target_lib = "mac_silicon"
    else:
        target_lib = "mac_intel"

if target_lib:
    lib_full_path = os.path.join(libs_path, target_lib)
    if lib_full_path not in sys.path:
        sys.path.insert(0, lib_full_path)

try:
    import zstandard as zstd
except ImportError as e:
    print(f"Error cargando zstandard para {system}/{machine}: {e}")
    zstd = None
