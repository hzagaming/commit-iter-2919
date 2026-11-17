#!/usr/bin/env python3
"""每次提交把版本号 +1，满 10000 进一位。

    python3 iter_commit.py --loop 30        # 每 30 秒提交一次
    python3 iter_commit.py --once           # 只提交一次
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
CHANGELOG = ROOT / "CHANGELOG.md"
STEP = 10_000
START = 2919


def version_for(n: int) -> str:
    """把迭代号换算成 主.次.修订 三段版本号，每段满 STEP 进位。"""
    if n < 0:
        raise ValueError("迭代号不能为负")
    major, rest = divmod(n, STEP ** 2)
    minor, patch = divmod(rest, STEP)
    if major == 0 and minor == 0:
        return f"0.0.{patch}"
    return f"{major}.{minor}.{patch:04d}"


def read_iter() -> int:
    if not VERSION_FILE.exists():
        return START
    text = VERSION_FILE.read_text(encoding="utf-8").strip()
    match = re.search(r"iter\s+(\d+)", text)
    return int(match.group(1)) if match else START


def git(*args: str) -> None:
    proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError((proc.stderr or proc.stdout).strip().splitlines()[-1])


def bump(n: int) -> str:
    version = version_for(n)
    VERSION_FILE.write_text(f"{version} (iter {n})\n", encoding="utf-8")
    with CHANGELOG.open("a", encoding="utf-8") as fh:
        fh.write(f"- v{version} · iter {n}\n")
    git("add", "VERSION", "CHANGELOG.md")
    git("commit", "-q", "-m", f"release: v{version} (iter {n})")
    return version


def push() -> None:
    for attempt in range(3):
        proc = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT,
                              capture_output=True, text=True)
        if proc.returncode == 0:
            return
        time.sleep(3 * (attempt + 1))
    print("推送失败，下次继续", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", type=float, default=0, help="每 N 秒提交一次，0 = 只跑一次")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    n = read_iter()
    while True:
        n += 1
        try:
            version = bump(n)
            push()
            print(f"{time.strftime('%H:%M:%S')} v{version} (iter {n})", flush=True)
        except RuntimeError as exc:
            print(f"提交失败: {exc}", flush=True)
            n -= 1
        if args.once or not args.loop:
            return
        time.sleep(args.loop)


if __name__ == "__main__":
    main()
