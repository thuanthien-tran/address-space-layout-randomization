#!/usr/bin/env python3
"""
Đo OFFSET_RET: khoảng cách từ &buffer tới ô lưu return address trong vuln().

Thứ tự mặc định (--method auto):
  1) GDB — breakpoint tại dòng read() trong aslr_demo.c
  2) LLDB — tương tự (một số máy Kali có lldb khi không cài được gdb)
  3) Probe C — biên dịch tools/vuln_stack_probe.c với cùng CFLAGS_NX như Makefile
     (chỉ cần gcc, không cần debugger)

Chạy từ thư mục gốc project:
  python3 tools/gdb_measure_offset.py              # ưu tiên aslr_demo_nx nếu đã build
  python3 tools/gdb_measure_offset.py --exec       # chỉ đo trên aslr_demo
  python3 tools/gdb_measure_offset.py --nx         # chỉ đo trên aslr_demo_nx
  python3 tools/gdb_measure_offset.py --binary PATH
  python3 tools/gdb_measure_offset.py --method probe   # bỏ qua gdb/lldb

Kali: nếu `sudo apt install gdb` báo "no installation candidate":
  sudo apt update
  sudo apt install gdb
  hoặc: sudo apt install lldb
  Hoặc để script tự chạy probe (gcc có sẵn trên Kali dev).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "exploits"))
from exploit_config import get_binary_nx_path, get_binary_path, get_demo_dir

# In ra log để phân biệt bản script (Kali “git pull” mà vẫn báo gdb-only = remote chưa có commit mới).
SCRIPT_VERSION = 3

# Khớp demo_aslr/Makefile: BASE_FLAGS + NX
PROBE_GCC_FLAGS = [
    "-O0",
    "-fno-omit-frame-pointer",
    "-fno-stack-protector",
    "-Wall",
    "-z",
    "noexecstack",
    "-no-pie",
]


def _vuln_input_line() -> int:
    path = os.path.join(ROOT, "demo_aslr", "aslr_demo.c")
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if "read(STDIN_FILENO, q, left)" in line:
                return i
    return 45


def _pick_binary(args: argparse.Namespace) -> str:
    if args.binary:
        return os.path.abspath(args.binary)
    nx = os.path.abspath(get_binary_nx_path())
    ex = os.path.abspath(get_binary_path())
    if args.nx_only:
        return nx
    if args.exec_only:
        return ex
    if os.path.isfile(nx):
        return nx
    return ex


def _measure_gdb(binary: str, cwd: str, line: int, src_dir: str) -> int | None:
    gdb = shutil.which("gdb")
    if not gdb:
        return None
    ex = [
        gdb,
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
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    except subprocess.CalledProcessError as e:
        out = e.output or b""
    text = out.decode(errors="replace")
    m = re.search(r"\$\d+ = (\d+)", text)
    return int(m.group(1)) if m else None


def _measure_lldb(binary: str, cwd: str, line: int) -> int | None:
    lldb = shutil.which("lldb")
    if not lldb:
        return None
    bin_base = os.path.basename(binary)
    ex = [
        lldb,
        "-b",
        "-o",
        f"file {bin_base}",
        "-o",
        f"breakpoint set --file aslr_demo.c --line {line}",
        "-o",
        "run",
        "-o",
        "expr (unsigned long)((char*)$rbp + 8 - (char*)&buffer)",
        "-o",
        "quit",
    ]
    try:
        out = subprocess.check_output(ex, cwd=cwd, stderr=subprocess.STDOUT, timeout=45)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    except subprocess.CalledProcessError as e:
        out = e.output or b""
    text = out.decode(errors="replace")
    m = re.search(r"(?:=\s*|=\s*\(unsigned long\)\s*\$\d+\s*=\s*)(\d+)\s*$", text, re.MULTILINE)
    if not m:
        m = re.search(r"\$\d+\s*=\s*(\d+)", text)
    return int(m.group(1)) if m else None


def _measure_probe() -> int | None:
    gcc = shutil.which("gcc")
    if not gcc:
        return None
    src = os.path.join(ROOT, "tools", "vuln_stack_probe.c")
    if not os.path.isfile(src):
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix="_probe") as tmp:
        exe = tmp.name
    try:
        r = subprocess.run(
            [gcc, *PROBE_GCC_FLAGS, "-o", exe, src],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode != 0:
            if r.stderr and r.stderr.strip():
                print(f"(probe) gcc stderr:\n{r.stderr}", file=sys.stderr)
            return None
        out = subprocess.check_output([exe], cwd=ROOT, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    finally:
        try:
            os.unlink(exe)
        except OSError:
            pass
    text = out.decode(errors="replace")
    m = re.search(r"OFFSET_RET_PROBE=(\d+)", text)
    return int(m.group(1)) if m else None


def _print_footer(off: int, binary: str, how: str) -> None:
    print()
    print("Sửa exploits/exploit_config.py:")
    print(f"  OFFSET_RET = {off}")
    print("  RET_DELTA = 0")
    print()
    print("Sau đó rebuild đúng bản bạn dùng:")
    print("  cd demo_aslr && make clean && make nx && cd ..")
    print("Kiểm tra Phase 1 (execstack): make && python3 -u exploits/exploit_phase1_aslr_off.py")
    print("Phase 4 (ROP): sudo sysctl -w kernel.randomize_va_space=2")
    print("  python3 exploits/exploit_phase4_rop.py")
    print("  hoặc: python3 exploits/exploit_phase4_rop.py all   # thử nhiều chuỗi ret")
    print()
    print(f"(Đo bằng: {how}; binary tham chiếu: {os.path.basename(binary)})")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Đo OFFSET_RET (buffer → saved RIP): GDB, LLDB hoặc probe C."
    )
    ap.add_argument(
        "--nx",
        dest="nx_only",
        action="store_true",
        help="Chỉ dùng demo_aslr/aslr_demo_nx (cần: make nx).",
    )
    ap.add_argument(
        "--exec",
        dest="exec_only",
        action="store_true",
        help="Chỉ dùng demo_aslr/aslr_demo (execstack, make mặc định).",
    )
    ap.add_argument("--binary", type=str, default=None, help="Đường dẫn tùy ý tới binary.")
    ap.add_argument(
        "--method",
        choices=("auto", "gdb", "lldb", "probe"),
        default="auto",
        help="auto: thử gdb → lldb → probe",
    )
    args = ap.parse_args()
    print(
        f"[*] gdb_measure_offset.py v{SCRIPT_VERSION} "
        "(có --method probe|gdb|lldb|auto — nếu không thấy dòng này thì file trên máy là bản cũ)",
        flush=True,
    )
    if args.nx_only and args.exec_only:
        print("Chỉ chọn một trong --nx hoặc --exec.", file=sys.stderr)
        return 2

    binary = _pick_binary(args)
    cwd = get_demo_dir()
    if not os.path.isfile(binary):
        hint = "make nx" if args.nx_only or binary.endswith("aslr_demo_nx") else "cd demo_aslr && make"
        print(f"Không thấy binary: {binary}\nChạy: {hint}", file=sys.stderr)
        return 1

    line = _vuln_input_line()
    src_dir = os.path.join(ROOT, "demo_aslr")

    off: int | None = None
    how = ""

    if args.method == "gdb":
        off = _measure_gdb(binary, cwd, line, src_dir)
        how = "GDB"
        if off is None:
            print("GDB không chạy được hoặc không parse được offset.", file=sys.stderr)
            return 1
    elif args.method == "lldb":
        off = _measure_lldb(binary, cwd, line)
        how = "LLDB"
        if off is None:
            print("LLDB không chạy được hoặc không parse được offset.", file=sys.stderr)
            return 1
    elif args.method == "probe":
        off = _measure_probe()
        how = "probe C (vuln_stack_probe.c, cùng CFLAGS NX như Makefile)"
        if off is None:
            print(
                "Probe thất bại (cần gcc và tools/vuln_stack_probe.c).",
                file=sys.stderr,
            )
            return 1
    else:
        off = _measure_gdb(binary, cwd, line, src_dir)
        if off is not None:
            how = "GDB"
        else:
            off = _measure_lldb(binary, cwd, line)
            if off is not None:
                how = "LLDB"
            else:
                off = _measure_probe()
                how = "probe C (vuln_stack_probe.c, cùng CFLAGS NX như Makefile)"

    if off is None:
        print(
            "Không đo được offset (không có gdb/lldb/gcc hoặc GDB/LLDB lỗi).\n"
            "Trên Kali nếu apt không có gdb:\n"
            "  sudo apt update && sudo apt install gdb\n"
            "  hoặc: sudo apt install lldb\n"
            "  hoặc cài đủ repo Kali (sources.list) rồi apt update.\n"
            "Nếu đã có gcc: thử  python3 tools/gdb_measure_offset.py --method probe",
            file=sys.stderr,
        )
        return 1

    print(f"Binary tham chiếu: {binary}")
    print(f"OFFSET_RET (đo {how}) = {off}")
    _print_footer(off, binary, how)
    return 0


if __name__ == "__main__":
    sys.exit(main())
