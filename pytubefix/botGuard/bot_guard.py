import os
import subprocess
import sys
import shutil
from typing import Optional

PLATFORM = sys.platform

NODE = 'node' if PLATFORM in ['linux', 'darwin'] else 'node.exe'

def _find_node_path() -> Optional[str]:
    """Try multiple ways to find Node.js path."""
    local_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f'binaries/{NODE}')
    if os.path.isfile(local_path):
        return local_path
    
    system_path = shutil.which(NODE)
    if system_path:
        return system_path
        
    return NODE

NODE_PATH = _find_node_path()
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
