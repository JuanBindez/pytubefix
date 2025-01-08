import os
import subprocess
import sys

PLATFORM = sys.platform

NODE = 'node' if PLATFORM == 'linux' else 'node.exe'

NODE_PATH = os.path.dirname(os.path.realpath(__file__)) + f'/binaries/{NODE}'

if not os.path.isfile(NODE_PATH):
    NODE_PATH = 'node'

VM_PATH = os.path.dirname(os.path.realpath(__file__)) + '/vm/botGuard.js'

def generate_po_token(visitor_data: str) -> str:
    """
    Run nodejs to generate poToken through botGuard.

    Requires nodejs installed.
    """
    result = subprocess.check_output(
        [NODE_PATH, VM_PATH, visitor_data]
    ).decode()
    return result.replace("\n", "")

