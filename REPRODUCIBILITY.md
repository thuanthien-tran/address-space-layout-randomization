# Reproducibility — Tái lập kết quả thực nghiệm

Tài liệu mô tả **môi trường và các bước chạy** để giảng viên hoặc người đọc có thể **tái lập** toàn bộ thực nghiệm đồ án. Đây là phần quan trọng cho tính nghiêm túc của đồ án.

---

## 1. Môi trường được kiểm tra

| Thành phần | Phiên bản / Ghi chú |
|------------|----------------------|
| **Hệ điều hành** | Ubuntu 22.04 LTS (64-bit) hoặc tương đương (20.04, 24.04). Có thể dùng VM hoặc WSL2. |
| **Kernel** | Linux 5.x trở lên (hỗ trợ `randomize_va_space`). |
| **Kiến trúc** | x86_64 (amd64). Script exploit và binary không dùng cho ARM/32-bit. |
| **GCC** | `gcc (Ubuntu 11.x–13.x)` hoặc tương đương. Lệnh kiểm tra: `gcc --version`. |
| **Python** | Python 3.8 trở lên. Lệnh kiểm tra: `python3 --version`. |
| **Tùy chọn** | `matplotlib` cho Giai đoạn 4 (histogram): `pip install matplotlib`. |

**Lưu ý:** Kết quả số (địa chỉ, entropy ước lượng) có thể khác nhẹ giữa máy/môi trường do ASLR; **hành vi** (ASLR OFF → địa chỉ cố định, ASLR ON → exploit fail / bypass thành công) phải tái lập được.

### 1.1 Environment specification (đặc tả môi trường rõ ràng)

Để tái lập **chặt chẽ**, ghi lại phiên bản cụ thể khi chạy thí nghiệm (có thể lưu vào file `environment_versions.txt` hoặc bảng trong báo cáo):

| Thành phần | Lệnh kiểm tra | Ví dụ giá trị (điền khi chạy) |
|------------|----------------|--------------------------------|
| **OS** | `lsb_release -a` hoặc `cat /etc/os-release` | Ubuntu 22.04.3 LTS |
| **Kernel** | `uname -r` | 5.15.0-91-generic |
| **Kiến trúc** | `uname -m` | x86_64 |
| **GCC** | `gcc --version` | gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0 |
| **Python** | `python3 --version` | Python 3.10.12 |
| **ASLR (khi chạy)** | `cat /proc/sys/kernel/randomize_va_space` | 0 (GĐ1) hoặc 2 (GĐ2–5) |

File mẫu **environment_versions.txt** (tạo bằng script hoặc tay):

```
OS: Ubuntu 22.04.3 LTS
Kernel: 5.15.0-91-generic
Arch: x86_64
GCC: 11.4.0
Python: 3.10.12
```

---

## 2. Các bước tái lập (theo thứ tự)

### 2.1 Clone / mở project và vào thư mục

```bash
cd "Address Space Layout Randomization"
cd demo_aslr
```

### 2.2 Build binary

```bash
make
# Tạo aslr_demo (no PIE). Cho GĐ5 thêm:
make pie
# Tạo aslr_demo_pie
```

**Kiểm tra:** `ls -la aslr_demo` (và `aslr_demo_pie` nếu đã `make pie`).

### 2.3 Giai đoạn 1 — Exploit khi ASLR OFF

```bash
sudo sysctl -w kernel.randomize_va_space=0
python3 ../exploits/exploit_phase1_aslr_off.py
```

**Kết quả mong đợi:** Output có dòng chứa `uid=...` (hoặc tương đương), và dòng `[+] EXPLOIT THÀNH CÔNG`.

### 2.4 Giai đoạn 2 — Exploit fail khi ASLR ON

```bash
# Bước 2.4a: Lấy địa chỉ cố định (vẫn ASLR=0)
./get_fixed_addr.sh
# Ghi lại địa chỉ 0x... ở dòng "Address of buffer"

# Bước 2.4b: Bật ASLR
sudo sysctl -w kernel.randomize_va_space=2

# Bước 2.4c: Chạy exploit với địa chỉ vừa ghi (thay 0x7ffc... bằng địa chỉ thực)
python3 ../exploits/exploit_phase2_aslr_on_fail.py --fixed-addr 0x7ffc00000000 --runs 50
```

**Kết quả mong đợi:** `Success: 0/50` (hoặc rất thấp). Phần lớn các lần chạy không in `uid=...`.

### 2.5 Giai đoạn 3 — Bypass bằng leak (ASLR vẫn = 2)

```bash
python3 ../exploits/exploit_phase3_bypass_leak.py
```

**Kết quả mong đợi:** Output có `uid=...` và dòng `[+] BYPASS THÀNH CÔNG`.

### 2.6 Giai đoạn 4 — Đo entropy (ASLR = 2)

```bash
python3 ../analysis/entropy_measurement.py --runs 500
```

**Kết quả mong đợi:** In ra thống kê (số mẫu, min/max, mô hình entropy H_unique/H_span, giải thích thống kê), tạo file `analysis/stack_addresses.csv` và (nếu có matplotlib) `analysis/entropy_histogram.png`. Thêm 95% CI: `--ci 500`.

### 2.7 Giai đoạn 5 — So sánh PIE vs non-PIE (ASLR = 2)

```bash
# Đảm bảo đã make pie
make both
python3 ../analysis/compare_pie.py --runs 5
```

**Kết quả mong đợi:** Bảng so sánh: non-PIE có địa chỉ main giống nhau giữa các lần; PIE có địa chỉ main khác nhau.

---

## 3. Tham số có thể thay đổi (và ảnh hưởng)

| Tham số | Mặc định | Ảnh hưởng khi đổi |
|---------|----------|--------------------|
| `--runs` (GĐ2, GĐ4) | 50 / 500 | Số lần chạy càng lớn, thống kê càng ổn định. |
| `--ci` (GĐ4) | 0 (tắt) | Nếu > 0 (vd. 500): bật 95% CI bootstrap cho entropy. |
| `--fixed-addr` (GĐ2) | Bắt buộc phải lấy từ `get_fixed_addr.sh` khi ASLR=0 trên **cùng máy** (cùng binary). |
| Kiến trúc / kernel khác | — | Địa chỉ và entropy có thể khác; hành vi ASLR ON/OFF và bypass vẫn giữ. |

---

## 4. Offsets kỹ thuật (tránh hard-code mù)

| Thành phần | Giá trị | Nơi định nghĩa / ghi chú |
|------------|---------|---------------------------|
| Kích thước buffer | 64 byte | `aslr_demo.c`: `char buffer[64]` |
| Offset tới return address | 72 byte | buffer(64) + saved RBP(8) trên x86-64. Định nghĩa **tập trung** trong `exploits/exploit_config.py` (BUFFER_SIZE, OFFSET_RET). |
| Shellcode | ~30 byte (x86-64 execve("/bin/sh")) | Trong `exploit_config.py`; có thể thay nếu đổi binary. |

Nếu thay đổi kích thước buffer trong C, cần chỉnh `OFFSET_RET` trong các script Python tương ứng.

---

## 5. Checklist tái lập (cho người chấm)

- [ ] Môi trường: Ubuntu (hoặc tương đương) x86_64, gcc, python3.
- [ ] Build: `make` (và `make pie` cho GĐ5) không lỗi.
- [ ] GĐ1: ASLR=0 → chạy exploit_phase1 → thấy success (uid=...).
- [ ] GĐ2: ASLR=2, fixed addr từ get_fixed_addr.sh → exploit_phase2 → success ≈ 0%.
- [ ] GĐ3: ASLR=2 → exploit_phase3_bypass_leak → thấy success.
- [ ] GĐ4: entropy_measurement.py → có CSV và (tùy chọn) histogram.
- [ ] GĐ5: compare_pie.py → bảng PIE vs non-PIE hợp lý.

---

**Thiết kế thí nghiệm chính thức** (giả thuyết, biến số, cỡ mẫu): xem **docs/EXPERIMENT_DESIGN.md**.

*Tài liệu này dùng cho báo cáo (phần "Tái lập thực nghiệm") và cho người chấm đồ án.*
