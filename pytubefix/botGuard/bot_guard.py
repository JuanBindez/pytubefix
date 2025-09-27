import os
import subprocess
import sys
import nodejs_wheel.executable

PLATFORM = sys.platform

NODE_DIR = nodejs_wheel.executable.ROOT_DIR

def _node_path() -> str:
    suffix = ".exe" if os.name == "nt" else ""
    bin_dir = NODE_DIR if os.name == "nt" else os.path.join(NODE_DIR, "bin")
    return os.path.join(bin_dir, 'node' + suffix)

NODE_PATH = _node_path()
VM_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vm/botGuard.js')

def generate_po_token(visitor_data: str) -> str:
    """
    Run nodejs to generate poToken through botGuard.
    
    Raises:
        RuntimeError: If Node.js is not available
    """
    try:
        result = subprocess.check_output(
            [NODE_PATH, VM_PATH, visitor_data],
            stderr=subprocess.PIPE
        ).decode()
        return result.replace("\n", "")
    except FileNotFoundError as e:
        raise RuntimeError(
            f"Node.js is required but not found. Tried path: {NODE_PATH}\n"
            "Please install Node.js or ensure it's in your PATH."
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to execute botGuard.js: {e.stderr.decode().strip()}"
        ) from e
