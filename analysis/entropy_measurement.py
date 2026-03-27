#!/usr/bin/env python3
"""
Giai đoạn 4 — Đo entropy ASLR (quantitative)
Chạy chương trình N lần (mặc định 500) khi ASLR bật, thu thập địa chỉ stack (buffer),
phân tích thống kê và vẽ phân phối (histogram).

Cách chạy (Linux):
  sudo sysctl -w kernel.randomize_va_space=2
  cd demo_aslr && make
  python3 ../analysis/entropy_measurement.py --runs 500

Output: CSV địa chỉ, thống kê (min/max/entropy ước lượng), và file histogram (nếu có matplotlib).
"""

import argparse
import os
import re
import subprocess
import sys

def parse_buffer_address(line: str):
    m = re.search(r"0x[0-9a-fA-F]+", line)
    if not m:
        return None
    return int(m.group(0), 16)


def collect_addresses(binary: str, cwd: str, runs: int):
    """Chạy binary `runs` lần, mỗi lần gửi input ngắn để không crash, thu địa chỉ buffer."""
    addrs = []
    for i in range(runs):
        proc = subprocess.Popen(
            [binary],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
        )
        proc.stdout.readline()
        proc.stdout.readline()
        line_buf = proc.stdout.readline().decode(errors="replace")
        proc.stdout.readline()
        proc.stdin.write(b"A\n")
        proc.stdin.close()
        proc.wait()
        addr = parse_buffer_address(line_buf)
        if addr is not None:
            addrs.append(addr)
        if (i + 1) % 100 == 0:
            print(f"    Thu thập {i + 1}/{runs}...", file=sys.stderr)
    return addrs


def main():
    ap = argparse.ArgumentParser(description="Đo entropy ASLR: thu thập địa chỉ stack, thống kê, vẽ histogram.")
    ap.add_argument("--runs", type=int, default=500, help="Số lần chạy (mặc định 500)")
    ap.add_argument("--binary", default="", help="Đường dẫn aslr_demo")
    ap.add_argument("--csv", default="stack_addresses.csv", help="File CSV xuất địa chỉ")
    ap.add_argument("--no-plot", action="store_true", help="Không vẽ histogram (không cần matplotlib)")
    ap.add_argument("--ci", type=int, default=0, metavar="N", help="Số mẫu bootstrap cho 95%% CI entropy (0=tắt, vd 500)")
    args = ap.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    binary = args.binary or os.path.join(project_root, "demo_aslr", "aslr_demo")
    if not os.path.isfile(binary):
        print("Không tìm thấy demo_aslr/aslr_demo. Chạy: cd demo_aslr && make", file=sys.stderr)
        sys.exit(1)
    cwd = os.path.dirname(binary)

    print("[*] Giai đoạn 4: Đo entropy ASLR (quantitative)")
    print(f"[*] ASLR phải BẬT (randomize_va_space=2). Chạy binary {args.runs} lần...")
    addrs = collect_addresses(binary, cwd, args.runs)
    if not addrs:
        print("Không thu được địa chỉ nào.", file=sys.stderr)
        sys.exit(1)

    # Thống kê
    import math
    import random
    addrs.sort()
    n = len(addrs)
    min_a, max_a = min(addrs), max(addrs)
    span = max_a - min_a
    unique = len(set(addrs))
    try:
        log2_unique = math.log2(unique) if unique > 0 else 0
        log2_span = math.log2(span) if span > 0 else 0
    except ValueError:
        log2_unique = log2_span = 0

    # Shannon entropy: H = -sum p_i log2(p_i) với p_i = tần suất địa chỉ i trong mẫu
    from collections import Counter
    counts = Counter(addrs)
    H_shannon = 0.0
    for addr, cnt in counts.items():
        p = cnt / n
        if p > 0:
            H_shannon -= p * math.log2(p)
    H_shannon_bits = H_shannon

    # 95% CI cho entropy (bootstrap): H = log2(K) với K = số unique trong resample
    ci_lo, ci_hi = None, None
    if args.ci > 0 and n > 0:
        bootstrap_entropies = []
        for _ in range(args.ci):
            resample = random.choices(addrs, k=n)
            k = len(set(resample))
            bootstrap_entropies.append(math.log2(k) if k > 0 else 0)
        bootstrap_entropies.sort()
        idx_lo = int(0.025 * args.ci)
        idx_hi = min(int(0.975 * args.ci), args.ci - 1)
        ci_lo, ci_hi = bootstrap_entropies[idx_lo], bootstrap_entropies[idx_hi]

    # Ghi CSV (thư mục analysis/)
    csv_path = os.path.join(script_dir, args.csv)
    os.makedirs(script_dir, exist_ok=True)
    with open(csv_path, "w") as f:
        f.write("run,address_hex,address_dec\n")
        for i, a in enumerate(addrs):
            f.write(f"{i+1},{hex(a)},{a}\n")
    print(f"[+] Đã ghi {n} địa chỉ vào {csv_path}")

    # In báo cáo (kèm mô hình entropy và giải thích thống kê)
    print()
    print("=== MÔ HÌNH ENTROPY (ước lượng) ===")
    print("  H_unique = log2(K) với K = số địa chỉ khác nhau trong mẫu.")
    print("  H_span   = log2(span) với span = max - min (cận trên độ rộng không gian).")
    print()
    print("=== PHÂN TÍCH THỐNG KÊ (Stack - địa chỉ buffer) ===")
    print(f"  Số mẫu:        {n}")
    print(f"  Địa chỉ khác nhau (K): {unique}")
    print(f"  Min:           {hex(min_a)}")
    print(f"  Max:           {hex(max_a)}")
    print(f"  Span:          {span} ({hex(span)})")
    print(f"  Entropy (từ K):     H_unique = log2(K) = {log2_unique:.2f} bit")
    print(f"  Entropy (từ span):  H_span   = log2(span) = {log2_span:.2f} bit (cận trên)")
    print(f"  Shannon entropy:     H_shannon = -sum p_i*log2(p_i) = {H_shannon_bits:.2f} bit")
    if ci_lo is not None and ci_hi is not None:
        print(f"  95% CI (bootstrap, n={args.ci}) cho H_unique: [{ci_lo:.2f}, {ci_hi:.2f}] bit")
    print()
    print("=== GIẢI THÍCH THỐNG KÊ ===")
    print("  Xác suất attacker đoán trúng 1 lần (trong K trạng thái) ≈ 1/K ≈ 2^(-H_unique).")
    prob = (1.0 / unique) if unique > 0 else 0.0
    print(f"  Với H ≈ {log2_unique:.1f} bit (K={unique}) → xác suất ≈ 1/K ≈ {prob:.2e}.")
    print("  → Càng nhiều bit entropy, exploit dùng địa chỉ cố định càng khó thành công (phù hợp GĐ2).")
    print()
    print("=== LIMITATIONS (giới hạn ước lượng) ===")
    print("  - Sample size N=%d chưa justify bằng power analysis; kết quả mang tính thực nghiệm." % n)
    print("  - Independence: các lần chạy coi là độc lập; có thể vi phạm trên một số kernel/loader.")
    print("  - Entropy phụ thuộc kiến trúc (x86-64) và kernel; không generalizable sang 32-bit/ARM.")
    print("  - H_unique = log2(K) là ước lượng số trạng thái quan sát được; H_shannon dùng phân phối empirical.")

    # Histogram (optional)
    if not args.no_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 4))
            plt.hist(addrs, bins=min(100, unique or 1), color="steelblue", edgecolor="black", alpha=0.7)
            plt.xlabel("Địa chỉ stack (buffer)")
            plt.ylabel("Số lần xuất hiện")
            plt.title("Phân phối địa chỉ stack khi ASLR bật (Giai đoạn 4)")
            plt.tight_layout()
            plot_path = os.path.join(script_dir, "entropy_histogram.png")
            plt.savefig(plot_path, dpi=150)
            plt.close()
            print(f"[+] Đã lưu histogram: {plot_path}")
        except ImportError:
            print("[*] Không có matplotlib — bỏ qua vẽ histogram. Có thể cài: pip install matplotlib")
        except Exception as e:
            print(f"[!] Lỗi khi vẽ: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
