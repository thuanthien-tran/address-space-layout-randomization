# Phân tích định lượng — Giai đoạn 4 & 5

## Giai đoạn 4: Đo entropy ASLR

**Script:** `entropy_measurement.py`

- Chạy binary (vd. 500 lần) khi **ASLR bật**, mỗi lần thu địa chỉ stack (buffer).
- Xuất **CSV** (`stack_addresses.csv`): cột run, address_hex, address_dec.
- In **thống kê:** H_unique = log2(K), H_span, **Shannon entropy** H = -sum p_i*log2(p_i), 95% CI (--ci 500), **Limitations**.
- Nếu cài `matplotlib`: vẽ **histogram** → `entropy_histogram.png`.

**Lệnh:**
```bash
sudo sysctl -w kernel.randomize_va_space=2
cd demo_aslr && make
python3 ../analysis/entropy_measurement.py --runs 500 --ci 500
```

**Ý nghĩa:** Formal entropy estimation (Shannon + log2(K)); xác suất đoán trúng ~ 2^(-H). Có nêu limitations (sample size, independence, architecture).

---

## Exploit success probability (mitigation evaluation)

**Script:** `exploit_success_probability.py`

- Chạy exploit **N lần (vd. 500)** khi ASLR OFF → success rate X%.
- Chạy exploit **N lần** khi ASLR ON (fixed addr) → success rate Y%.
- So sánh: **"ASLR reduces exploit success probability from X% to Y%"**; tùy chọn vẽ bar chart.

**Lệnh:**
```bash
cd demo_aslr && make
sudo sysctl -w kernel.randomize_va_space=0
python3 ../analysis/exploit_success_probability.py --phase both --runs 500
# (sẽ nhắc set ASLR=2 giữa chừng)
```

Hoặc tách: `--phase off --runs 500` (ghi lại fixed_addr) → set ASLR=2 → `--phase on --runs 500 --fixed-addr 0x...`.

**Ý nghĩa:** Mitigation evaluation chuẩn research — đo probability, không chỉ success/fail đơn lẻ.

---

## Mitigation matrix (điểm cộng báo cáo)

**Script:** `mitigation_matrix.py`

- Tạo bảng kết quả theo đúng flow mitigation:
  - No protection
  - ASLR only
  - ASLR + leak
  - ASLR + NX
  - ASLR + NX + ROP
- Dùng để chèn trực tiếp vào báo cáo phần kết luận defense.

**Lệnh:**
```bash
cd demo_aslr
python3 ../analysis/mitigation_matrix.py
```

---

## Giai đoạn 5: So sánh PIE vs non-PIE

**Script:** `compare_pie.py`

- Chạy **aslr_demo** (non-PIE) và **aslr_demo_pie** (PIE) mỗi binary vài lần khi ASLR=2.
- Thu địa chỉ **main** và **buffer**, in bảng so sánh.
- **Nhận xét:** Non-PIE → main cố định; PIE → main thay đổi → khó khai thác hơn (executable cũng random).

**Lệnh:**
```bash
cd demo_aslr && make both
sudo sysctl -w kernel.randomize_va_space=2
python3 ../analysis/compare_pie.py --runs 5
```

---

Output (CSV, PNG) có thể đưa trực tiếp vào báo cáo và slide.
