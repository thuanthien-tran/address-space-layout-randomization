#!/usr/bin/env python3
"""
Đo OFFSET_RET (khoảng cách &buffer → saved RIP) CHỈ bằng gcc — không cần gdb/lldb/binary demo.

Dùng khi:
  - apt Kali lỗi GPG / không cài được gdb
  - git pull vẫn là bản cũ (chưa push tools mới lên remote)

Chạy (bất kỳ thư mục nào, chỉ cần 1 file này + gcc):
  python3 offset_probe_standalone.py

Có thể copy file sang Kali:
  scp tools/offset_probe_standalone.py kali@...:/tmp/
  python3 /tmp/offset_probe_standalone.py
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile

# Khớp demo_aslr/Makefile: BASE_FLAGS + -z noexecstack -no-pie
GCC_FLAGS = [
    "-O0",
    "-fno-omit-frame-pointer",
    "-fno-stack-protector",
    "-Wall",
    "-z",
    "noexecstack",
    "-no-pie",
]

# Khớp khối (q, left, n) trong vuln() aslr_demo.c ngay trước vòng while read.
PROBE_C = r"""
#include <stddef.h>
#include <stdio.h>
#include <sys/types.h>
static void vuln(void *heap_ptr) {
    char buffer[64];

    printf("Address of buffer: %p (stack)\n", (void *)buffer);
    printf("Address of heap:   %p (heap/malloc)\n", heap_ptr);
    fflush(stdout);

    {
        unsigned char *q = (unsigned char *)buffer;
        size_t left = 400;
        ssize_t n = 0;
        (void)n;
        printf(
            "OFFSET_RET_PROBE=%zu\n",
            (size_t)(((unsigned char *)__builtin_frame_address(0) + 8)
                     - (unsigned char *)&buffer));
        (void)q;
        (void)left;
    }
}
int main(void) {
    vuln((void *)0);
    return 0;
}
"""


def main() -> int:
    gcc = shutil.which("gcc")
    if not gcc:
        print("Không tìm thấy gcc. Cài build-essential hoặc gcc.", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "probe.c")
        exe = os.path.join(td, "probe")
        with open(src, "w", encoding="utf-8") as f:
            f.write(PROBE_C)
        try:
            r = subprocess.run(
                [gcc, *GCC_FLAGS, "-o", exe, src],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except OSError as e:
            print(f"gcc lỗi: {e}", file=sys.stderr)
            return 1
        if r.returncode != 0:
            print("gcc biên dịch thất bại:", file=sys.stderr)
            print(r.stderr or r.stdout, file=sys.stderr)
            return 1
        try:
            out = subprocess.check_output([exe], timeout=5)
        except subprocess.CalledProcessError as e:
            print("Chạy probe thất bại:", e, file=sys.stderr)
            return 1

    text = out.decode(errors="replace")
    m = re.search(r"OFFSET_RET_PROBE=(\d+)", text)
    if not m:
        print("Không parse được output:", repr(text), file=sys.stderr)
        return 1
    off = int(m.group(1))
    print("[*] offset_probe_standalone.py — không cần gdb")
    print(f"OFFSET_RET (probe C, cùng CFLAGS NX như Makefile) = {off}")
    print()
    print("Sửa exploits/exploit_config.py:")
    print(f"  OFFSET_RET = {off}")
    print("  RET_DELTA = 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
