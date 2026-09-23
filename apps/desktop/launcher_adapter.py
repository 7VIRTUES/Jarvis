"""Desktop-only policy adapter; all runtime startup stays in jarvis_launcher."""

from pathlib import Path
import os
import subprocess
import sys
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener


class LocalHealthOnly(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise URLError("Desktop health redirects are disabled")


class NonInteractiveProcesses:
    """Keep launcher children hidden, with valid null standard handles."""

    def __getattr__(self, name):
        return getattr(subprocess, name)

    @staticmethod
    def options(kwargs):
        return {
            **kwargs,
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "creationflags": subprocess.CREATE_NO_WINDOW,
            "shell": False,
        }

    def Popen(self, *args, **kwargs):
        return subprocess.Popen(*args, **self.options(kwargs))

    def run(self, *args, **kwargs):
        return subprocess.run(*args, **self.options(kwargs))


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "scripts"))
    import jarvis_launcher as launcher

    # No console, interactive setup, installation, or persistent desktop logs.
    sys.stdin = open(os.devnull, "r")
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")

    opener = build_opener(ProxyHandler({}), LocalHealthOnly())

    def local_health_open(url, timeout):
        if url != "http://127.0.0.1:8000/health":
            raise URLError("Only the fixed desktop health URL is allowed")
        return opener.open(url, timeout=timeout)

    launcher.urlopen = local_health_open
    launcher.subprocess = NonInteractiveProcesses()
    # The standard launcher configures generation/embeddings even on reuse.
    # Desktop launch must be read-only toward any existing instance, including
    # one that wins a port race. Keep its settings; never invoke bootstrap here.
    launcher.configure_services_if_available = lambda port: None
    return launcher.main(["--no-browser"])


if __name__ == "__main__":
    raise SystemExit(main())
