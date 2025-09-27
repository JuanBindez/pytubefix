import os
import json
import subprocess
import nodejs_wheel.executable


RUNNER_PATH = os.path.join(os.path.dirname(__file__), "vm", "runner.js")
NODE_DIR = nodejs_wheel.executable.ROOT_DIR

class NodeRunner:
    def __init__(self, code: str):
        self.code = code
        self.function_name = None
        self.proc = subprocess.Popen(
            [self._node_path(), RUNNER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

    @staticmethod
    def _node_path() -> str:
        suffix = ".exe" if os.name == "nt" else ""
        bin_dir = NODE_DIR if os.name == "nt" else os.path.join(NODE_DIR, "bin")
        return os.path.join(bin_dir, 'node' + suffix)

    @staticmethod
    def _exposed(code: str, fun_name: str) -> str:
        exposed = f"_exposed['{fun_name}']={fun_name};" + "})(_yt_player);"
        return code.replace("})(_yt_player);", exposed)

    def _send(self, data):
        self.proc.stdin.write(json.dumps(data) + "\n")
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def load_function(self, function_name: str):
        self.function_name = function_name
        return self._send({"type": "load", "code": self._exposed(self.code, function_name)})

    def call(self, args: list):
        return self._send({"type": "call", "fun": self.function_name, "args": args or []})

    def close(self):
        self.proc.stdin.close()
        self.proc.terminate()
        self.proc.wait()