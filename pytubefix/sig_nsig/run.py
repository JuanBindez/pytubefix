import subprocess
import json
import sys
import os


def _exposed(code: str, fun_name: str) -> str:
    exposed = f"_exposed['{fun_name}']={fun_name};" + "})(_yt_player);"
    return code.replace("})(_yt_player);", exposed)


def run_js_interpreter(full_code: str, fun_name: str, args: list):
    try:
        payload = {
            "full_code": _exposed(full_code, fun_name),
            "fun_name": fun_name,
            "args": args
        }

        # Build absolute path to runner.js inside the installed package
        runner_path = os.path.join(os.path.dirname(__file__), "vm", "runner.js")

        process = subprocess.Popen(
            ['node', runner_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        stdout, stderr = process.communicate(json.dumps(payload))

        if process.returncode != 0:
            print(stderr)
            return None

        result = json.loads(stdout)
        return result.get('result')

    except FileNotFoundError:
        sys.exit(1)
    except Exception as e:
        return None
