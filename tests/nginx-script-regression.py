#!/usr/bin/env python3
"""Check the script-code regression from #785 against the installed Nginx."""

import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request


EXPECTED_KEY = "nginx-cache%3AhttpGET127.0.0.1%2F%3Fa%3D1%26b%3D2\n"
CRASH = re.compile(r"exited on signal|segfault|core dumped", re.I)


def worker_pids(master):
    output = subprocess.run(["ps", "-o", "pid=", "--ppid", str(master.pid)],
                            text=True, capture_output=True)
    if output.returncode not in (0, 1):
        raise RuntimeError(output.stderr)
    return sorted(int(pid) for pid in output.stdout.split())


def group_pids(group):
    output = subprocess.check_output(["ps", "-eo", "pid=,pgid="], text=True)
    return [int(pid) for pid, pgid in (line.split() for line in output.splitlines())
            if int(pgid) == group]


def stop_instance(master):
    # start_new_session keeps cleanup separate from the installed Nginx service.
    for sig, seconds in [(signal.SIGQUIT, 5), (signal.SIGTERM, 2), (signal.SIGKILL, 2)]:
        master.poll()
        if not group_pids(master.pid):
            return
        try:
            os.killpg(master.pid, sig)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            master.poll()
            if not group_pids(master.pid):
                return
            time.sleep(0.05)
    raise RuntimeError("Probe processes remain after shutdown")


def check_response(opener, port, path, expected):
    with opener.open(f"http://127.0.0.1:{port}{path}", timeout=5) as response:
        body = response.read().decode("utf-8")
        if response.status != 200 or body != expected:
            raise AssertionError(f"{path}: HTTP {response.status}, body {body!r}; expected {expected!r}")


def probe():
    if sys.platform != "linux":
        raise RuntimeError("Run this test in the disposable Linux CI environment")
    subprocess.run(["nginx", "-V"], check=True)
    with tempfile.TemporaryDirectory(prefix="wordops-nginx-script-") as directory:
        root = Path(directory)
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        (root / "nginx.conf").write_text(f'''daemon off;
master_process on;
worker_processes 1;
pid nginx.pid;
error_log error.log info;
events {{ worker_connections 128; }}
http {{
    access_log access.log;
    server {{
        listen 127.0.0.1:{port};
        location / {{
            set $key "nginx-cache:$scheme$request_method$host$request_uri";
            set_escape_uri $escaped_key $key;
            return 200 "$escaped_key\\n";
        }}
        location = /bypass {{ return 200 "bypass\\n"; }}
    }}
}}
''')
        command = ["nginx", "-p", f"{root}/", "-c", "nginx.conf", "-e", str(root / "error.log")]
        master = None
        failures = []
        with (root / "output.log").open("w") as output:
            try:
                subprocess.run(command + ["-t"], stdout=output, stderr=output, check=True)
                master = subprocess.Popen(command, stdout=output, stderr=output, start_new_session=True)
                deadline = time.monotonic() + 10
                while True:
                    if master.poll() is not None:
                        raise RuntimeError("Nginx exited during startup")
                    workers = worker_pids(master)
                    if len(workers) == 1:
                        break
                    if time.monotonic() >= deadline:
                        raise RuntimeError("One Nginx worker did not start within 10 seconds")
                    time.sleep(0.05)
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                check_response(opener, port, "/bypass", "bypass\n")
                for _ in range(100):
                    check_response(opener, port, "/?a=1&b=2", EXPECTED_KEY)
                    if master.poll() is not None or worker_pids(master) != workers:
                        raise AssertionError("Nginx worker changed during repeated cache-key requests")
                check_response(opener, port, "/bypass", "bypass\n")
                if master.poll() is not None or worker_pids(master) != workers:
                    raise AssertionError("Nginx worker did not survive all requests")
            except Exception as error:
                failures.append(f"{type(error).__name__}: {error}")
            finally:
                if master is not None:
                    try:
                        stop_instance(master)
                    except Exception as error:
                        failures.append(f"Cleanup failed: {error}")
        log = root / "error.log"
        if not log.exists():
            failures.append("Nginx error log is missing")
        elif CRASH.search(log.read_text(errors="replace")):
            failures.append("Nginx crash signature in error log")
        if failures:
            for name in ["output.log", "error.log", "access.log"]:
                path = root / name
                if path.exists():
                    print(f"--- {name} ---\n{path.read_text(errors='replace')}", file=sys.stderr)
            raise RuntimeError("; ".join(failures))
    print("Nginx script regression: HTTP 200, correct escaped key, 100 requests with one stable worker passed")


if __name__ == "__main__":
    try:
        probe()
    except Exception as error:
        print(f"Nginx script regression FAILED: {error}", file=sys.stderr)
        sys.exit(1)
