#!/usr/bin/env python3
"""
Mitigation matrix runner:
  No protection | ASLR only | ASLR+leak | ASLR+NX | ASLR+NX+ROP

Script này không đổi sysctl tự động; chỉ nhắc bạn set ASLR đúng trước mỗi bước.
"""

import os
import re
import subprocess
import sys
import argparse


def run_cmd(args, cwd):
    p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()[0].decode(errors="replace")
    return p.returncode, out


def has_uid(output: str):
    # Chỉ khớp output kiểu `id` (uid=1000...), tránh nhầm với "Chưa thấy uid="
    return bool(re.search(r"uid=\d+", output))


def main():
    ap = argparse.ArgumentParser(description="Run mitigation comparison matrix.")
    ap.add_argument("--fixed-addr", default="", help="Fixed buffer address for ASLR-only/NX shellcode cases.")
    ap.add_argument("--non-interactive", action="store_true", help="Do not wait for Enter prompts.")
    args = ap.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    demo_dir = os.path.join(project_root, "demo_aslr")

    rows = []

    print("=== CASE 1: No protection (ASLR=0, execstack) ===")
    print("Set: sudo sysctl -w kernel.randomize_va_space=0")
    if not args.non_interactive:
        input("Nhấn Enter sau khi set xong...")
    code, out = run_cmd(["python3", "../exploits/exploit_phase1_aslr_off.py"], demo_dir)
    rows.append(("No protection", "shellcode", "SUCCESS" if has_uid(out) else "FAIL"))

    print("=== CASE 2: ASLR only (ASLR=2, fixed addr) ===")
    print("Set: sudo sysctl -w kernel.randomize_va_space=2")
    fixed = args.fixed_addr.strip()
    if not fixed:
        fixed = input("Nhập fixed_addr (lấy từ get_fixed_addr.sh): ").strip()
    code, out = run_cmd(
        ["python3", "../exploits/exploit_phase2_aslr_on_fail.py", "--fixed-addr", fixed, "--runs", "50"], demo_dir
    )
    m = re.search(r"Success:\s*(\d+)/(\d+)", out)
    aslr_only_fail = (not m) or int(m.group(1)) == 0
    rows.append(
        ("ASLR only", "fixed-address shellcode", "FAIL" if aslr_only_fail else "SUCCESS")
    )

    print("=== CASE 3: ASLR + leak ===")
    code, out = run_cmd(["python3", "../exploits/exploit_phase3_bypass_leak.py"], demo_dir)
    rows.append(("ASLR + leak", "leak + shellcode", "SUCCESS" if has_uid(out) else "FAIL"))

    print("=== CASE 4: ASLR + NX (shellcode expected fail) ===")
    run_cmd(["make", "nx"], demo_dir)
    code, out = run_cmd(
        ["python3", "../exploits/exploit_phase2_aslr_on_fail.py", "--fixed-addr", fixed, "--runs", "20", "--binary", "./aslr_demo_nx"],
        demo_dir,
    )
    rows.append(("ASLR + NX", "shellcode", "FAIL" if not has_uid(out) else "SUCCESS"))

    print("=== CASE 5: ASLR + NX + ROP ===")
    code, out = run_cmd(["python3", "../exploits/exploit_phase4_rop.py"], demo_dir)
    rows.append(("ASLR + NX + ROP", "ret2libc", "SUCCESS" if has_uid(out) else "FAIL"))

    print("\n=== MITIGATION MATRIX ===")
    print(f"{'Case':<20} {'Exploit':<24} {'Result':<10}")
    print("-" * 56)
    for c, e, r in rows:
        print(f"{c:<20} {e:<24} {r:<10}")
    print("\nKết luận gợi ý: ASLR alone is not sufficient without other mitigations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
