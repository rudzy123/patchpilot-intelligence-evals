"""Resource fixtures. Each mode exceeds one limit and prints a short status."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path


def main() -> None:
    mode = sys.argv[1]
    if mode == "memory":
        try:
            blob = bytearray(180 * 1024 * 1024)
            print("ALLOC", len(blob))
        except MemoryError:
            print("MEMORYERROR")
        return
    if mode == "cpu":
        while True:
            pass
    if mode == "file-size":
        try:
            Path("/results/big").write_bytes(b"x")
            print("WROTE")
        except OSError:
            print("FILESIZE")
        return
    if mode == "open-files":
        opened: list[object] = []
        try:
            while True:
                opened.append(open("/dev/null", "rb"))
        except OSError:
            print("NOFILE")
        return
    if mode == "tasks":
        count = 0
        try:
            for _index in range(20):
                pid = os.fork()
                if pid == 0:
                    time.sleep(30)
                    os._exit(0)
                count += 1
            print("FORKS", count)
        except OSError:
            print("TASKS")
        return
    if mode == "wall":
        time.sleep(30)
        print("SLEPT")
        return
    if mode == "stdout":
        sys.stdout.write("x" * 200000)
        sys.stdout.flush()
        return
    if mode == "stderr":
        sys.stderr.write("y" * 200000)
        sys.stderr.flush()
        return
    if mode == "tree":
        token = sys.argv[2]
        pid = os.fork()
        if pid == 0:
            os.setsid()
            os.execv(sys.executable, [sys.executable, "-c", "import time; time.sleep(30)", token])
        time.sleep(30)
        return
    if mode == "ok":
        Path("/results/ok.txt").write_text("ok", encoding="utf-8")
        print("OK")
        return
    raise SystemExit(2)


if __name__ == "__main__":
    main()
