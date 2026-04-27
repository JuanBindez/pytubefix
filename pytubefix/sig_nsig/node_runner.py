import os
import json
import subprocess
import nodejs_wheel.executable


RUNNER_PATH = os.path.join(os.path.dirname(__file__), "vm", "runner.js")
NODE_DIR = nodejs_wheel.executable.ROOT_DIR


class NodeRunnerError(Exception):
    """Base exception for NodeRunner process/response failures."""


class NodeRunnerEmptyResponseError(NodeRunnerError):
    """Raised when the runner returns EOF or a blank line instead of JSON."""


class NodeRunnerUndefinedResponseError(NodeRunnerError):
    """Raised when the runner returns the literal JavaScript `undefined`."""


class NodeRunnerInvalidResponseError(NodeRunnerError):
    """Raised when the runner returns a non-JSON payload."""


class NodeRunner:
    def __init__(self, code: str):
        self.code = code
        self.function_name = None
        self.proc = None
        self._start_process()

    def _start_process(self):
        self.proc = subprocess.Popen(
            [self._node_path(), RUNNER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
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

    def is_running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def restart(self):
        function_name = self.function_name
        self.close()
        self._start_process()
        if function_name:
            self.load_function(function_name)

    def _send(self, data):
        if not self.is_running():
            self.restart()
        self.proc.stdin.write(json.dumps(data) + "\n")
        self.proc.stdin.flush()
        raw_line = self.proc.stdout.readline()
        if raw_line == "":
            raise NodeRunnerEmptyResponseError("Node runner returned EOF")

        line = raw_line.strip()
        if not line:
            raise NodeRunnerEmptyResponseError("Node runner returned a blank line")
        if line == "undefined":
            raise NodeRunnerUndefinedResponseError("Node runner returned undefined")

        try:
            return json.loads(line)
        except json.JSONDecodeError as exc:
            snippet = line[:200]
            raise NodeRunnerInvalidResponseError(
                f"Node runner returned non-JSON output: {snippet}"
            ) from exc

    def load_function(self, function_name: str):
        self.function_name = function_name
        return self._send({"type": "load", "code": self._exposed(self.code, function_name)})

    def call(self, args: list):
        return self._send({"type": "call", "fun": self.function_name, "args": args or []})

    def close(self):
        proc = self.proc
        self.proc = None
        if proc is None:
            return
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except Exception:
            pass
        try:
            if proc.poll() is None:
                proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
                proc.wait(timeout=2)
            except Exception:
                pass
