#!/usr/bin/env python3
"""
Đo OFFSET_RET bằng GDB: khoảng cách từ &buffer tới ô lưu return address.

Breakpoint đặt tại dòng read(STDIN_FILENO, buffer, ...) (sau khi frame vuln đã dựng xong).

Chạy từ thư mục gốc project:
  python3 tools/gdb_measure_offset.py

Yêu cầu: gdb (sudo apt install gdb)
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "exploits"))
from exploit_config import get_binary_path, get_demo_dir


def _vuln_input_line() -> int:
    path = os.path.join(ROOT, "demo_aslr", "aslr_demo.c")
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if "read(STDIN_FILENO, buffer" in line:
                return i
    return 41


def main() -> int:
    binary = os.path.abspath(get_binary_path())
    cwd = get_demo_dir()
    if not os.path.isfile(binary):
        print("Không thấy binary. Chạy: cd demo_aslr && make", file=sys.stderr)
        return 1

    line = _vuln_input_line()
    src_dir = os.path.join(ROOT, "demo_aslr")

    ex = [
        "gdb",
        "-q",
        "-batch",
        "-ex",
        f"directory {src_dir}",
        "-ex",
        f"break aslr_demo.c:{line}",
        "-ex",
        "run </dev/null",
        "-ex",
        "print (unsigned long)((char*)$rbp + 8 - (char*)&buffer)",
        "-ex",
        "quit",
        binary,
    ]

    try:
        out = subprocess.check_output(ex, cwd=cwd, stderr=subprocess.STDOUT, timeout=45)
    except FileNotFoundError:
        print("Không tìm thấy gdb. Cài: sudo apt install gdb", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        out = e.output or b""

    text = out.decode(errors="replace")
    m = re.search(r"\$\d+ = (\d+)", text)
    if not m:
        print("GDB không trả offset. Output:\n", text, file=sys.stderr)
        print("", file=sys.stderr)
        print("Thử: gdb ./demo_aslr/aslr_demo  rồi:", file=sys.stderr)
        print(f"  break aslr_demo.c:{line}", file=sys.stderr)
        print("  run </dev/null", file=sys.stderr)
        print("  print (unsigned long)((char*)$rbp + 8 - (char*)&buffer)", file=sys.stderr)
        return 1

    off = int(m.group(1))
    print(f"OFFSET_RET (đo GDB) = {off}")
    print()
    print("Sửa exploits/exploit_config.py:")
    print(f"  OFFSET_RET = {off}")
    print("  RET_DELTA = 0")
    print()
    print("Sau đó: cd demo_aslr && make clean && make && cd ..")
    print("        python3 -u exploits/exploit_phase1_aslr_off.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
