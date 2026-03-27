#!/usr/bin/env python3
"""
Giai đoạn 5 — So sánh PIE vs non-PIE
Chạy cả aslr_demo (non-PIE) và aslr_demo_pie (PIE) nhiều lần khi ASLR=2,
thu thập địa chỉ main và buffer, in bảng so sánh.

Cách chạy (Linux):
  sudo sysctl -w kernel.randomize_va_space=2
  cd demo_aslr && make both
  python3 ../analysis/compare_pie.py --runs 5
"""

import argparse
import os
import re
import subprocess
import sys


def parse_address(line: str):
    m = re.search(r"0x[0-9a-fA-F]+", line)
    return int(m.group(0), 16) if m else None


def run_and_parse(binary: str, cwd: str, input_line: bytes = b"X\n"):
    """Chạy binary, gửi input_line, trả về (main_addr, printf_addr, buffer_addr, heap_addr) hoặc None."""
    proc = subprocess.Popen(
        [binary],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
    )
    main_line = proc.stdout.readline().decode(errors="replace")
    printf_line = proc.stdout.readline().decode(errors="replace")
    buffer_line = proc.stdout.readline().decode(errors="replace")
    heap_line = proc.stdout.readline().decode(errors="replace")
    proc.stdin.write(input_line)
    proc.stdin.close()
    proc.wait()
    main_a = parse_address(main_line)
    buffer_a = parse_address(buffer_line)
    return main_a, buffer_a


def main():
    ap = argparse.ArgumentParser(description="So sánh PIE vs non-PIE: địa chỉ main và buffer khi ASLR=2.")
    ap.add_argument("--runs", type=int, default=5, help="Số lần chạy mỗi binary")
    args = ap.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    demo_dir = os.path.join(project_root, "demo_aslr")
    binary_no_pie = os.path.join(demo_dir, "aslr_demo")
    binary_pie = os.path.join(demo_dir, "aslr_demo_pie")

    if not os.path.isfile(binary_no_pie):
        print("Chưa có aslr_demo. Chạy: cd demo_aslr && make", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(binary_pie):
        print("Chưa có aslr_demo_pie. Chạy: cd demo_aslr && make pie", file=sys.stderr)
        sys.exit(1)

    print("[*] Giai đoạn 5: So sánh PIE vs non-PIE (ASLR=2)")
    print(f"[*] Chạy mỗi binary {args.runs} lần...\n")

    no_pie_main = []
    no_pie_buf = []
    for _ in range(args.runs):
        m, b = run_and_parse(binary_no_pie, demo_dir)
        if m is not None:
            no_pie_main.append(m)
        if b is not None:
            no_pie_buf.append(b)

    pie_main = []
    pie_buf = []
    for _ in range(args.runs):
        m, b = run_and_parse(binary_pie, demo_dir)
        if m is not None:
            pie_main.append(m)
        if b is not None:
            pie_buf.append(b)

    print("=== BẢNG SO SÁNH: Địa chỉ main (executable) khi ASLR=2 ===")
    print("  Non-PIE (aslr_demo):     main CỐ ĐỊNH giữa các lần chạy")
    if no_pie_main:
        uniq = len(set(no_pie_main))
        print(f"    Các giá trị: {[hex(x) for x in no_pie_main[:5]]}{'...' if len(no_pie_main) > 5 else ''} — số giá trị khác nhau: {uniq}")
    print("  PIE (aslr_demo_pie):     main THAY ĐỔI mỗi lần chạy")
    if pie_main:
        uniq = len(set(pie_main))
        print(f"    Các giá trị: {[hex(x) for x in pie_main[:5]]}{'...' if len(pie_main) > 5 else ''} — số giá trị khác nhau: {uniq}")
    print()
    print("=== BẢNG SO SÁNH: Địa chỉ buffer (stack) khi ASLR=2 ===")
    print("  Cả hai: stack đều random (ASLR ảnh hưởng stack).")
    if no_pie_buf:
        print(f"  Non-PIE buffer: {[hex(x) for x in no_pie_buf[:5]]}{'...' if len(no_pie_buf) > 5 else ''}")
    if pie_buf:
        print(f"  PIE buffer:    {[hex(x) for x in pie_buf[:5]]}{'...' if len(pie_buf) > 5 else ''}")
    print()
    print("KẾT LUẬN:")
    print("  - Non-PIE: attacker vẫn biết địa chỉ code (main, gadget) → ROP trong executable dễ hơn.")
    print("  - PIE: code cũng random → khó khai thác hơn (entropy toàn bộ không gian địa chỉ).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
