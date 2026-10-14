"""Download the Pyodide runtime into static/vendor/pyodide so coding challenges work on a classroom
network with no internet (same as the Sets app). The worker falls back to the CDN if this copy is missing.

    python scripts/vendor_pyodide.py
"""
import os
import sys
import urllib.request

VERSION = "0.26.4"  # same version the Sets app ships
CDN = f"https://cdn.jsdelivr.net/pyodide/v{VERSION}/full/"
FILES = ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "vendor", "pyodide")


def main():
    os.makedirs(DEST, exist_ok=True)
    for name in FILES:
        path = os.path.join(DEST, name)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"have  {name} ({os.path.getsize(path):,} B)")
            continue
        tmp = path + ".part"
        with urllib.request.urlopen(CDN + name, timeout=120) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 16):
                f.write(chunk)
        os.replace(tmp, path)
        print(f"got   {name} ({os.path.getsize(path):,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
