# Experiment design — Thiết kế thí nghiệm chính thức

Tài liệu mô tả **thiết kế thí nghiệm** cho đánh giá hiệu quả ASLR: giả thuyết, biến số, yếu tố kiểm soát và cỡ mẫu. Giúp báo cáo có **formal experiment design** và reproducibility rõ ràng.

---

## 1. Mục tiêu thí nghiệm

Đánh giá **hiệu quả mitigation ASLR** trong việc làm giảm tính ổn định của exploit buffer overflow (overwrite return address, shellcode), và đánh giá **ảnh hưởng của information leak** cùng **PIE**.

---

## 2. Giả thuyết (hypotheses)

| ID | Giả thuyết | Cách kiểm chứng |
|----|------------|------------------|
| **H1** | Khi ASLR tắt, exploit dùng địa chỉ buffer cố định sẽ **thành công ổn định** (success rate cao). | GĐ1: chạy exploit khi randomize_va_space=0; đo success (có shell / uid). |
| **H2** | Khi ASLR bật và attacker **không** có leak, exploit dùng địa chỉ cố định sẽ **thất bại** (success rate ≈ 0%). | GĐ2: ASLR=2, payload dùng fixed addr; chạy N lần, đếm success. |
| **H3** | Khi ASLR bật nhưng attacker **có** leak địa chỉ buffer, exploit có thể **bypass** và thành công. | GĐ3: ASLR=2, đọc leak từ stdout, dùng làm RET; đo success. |
| **H4** | Địa chỉ stack (buffer) khi ASLR bật có **phân phối phân tán** với entropy ước lượng > 0 (định lượng). | GĐ4: thu N địa chỉ, tính K (unique), H = log2(K), có thể 95% CI. |
| **H5** | Khi ASLR bật, binary **PIE** có địa chỉ main thay đổi giữa các lần chạy; binary **non-PIE** có main cố định. | GĐ5: so sánh số giá trị địa chỉ main giữa aslr_demo và aslr_demo_pie. |

---

## 3. Biến số (variables)

| Loại | Tên | Mô tả | Giá trị trong thí nghiệm |
|------|-----|--------|----------------------------|
| **Độc lập** | ASLR | Mức ASLR (kernel) | 0 (tắt), 2 (bật) |
| **Độc lập** | Có leak / không leak | Attacker có đọc được địa chỉ buffer không | GĐ1/GĐ2: không; GĐ3: có |
| **Độc lập** | PIE | Binary có PIE hay không | aslr_demo (no), aslr_demo_pie (yes) |
| **Phụ thuộc** | Success (exploit) | Có mở được shell (vd. output có uid) hay không | Boolean mỗi lần chạy |
| **Phụ thuộc** | Entropy (stack) | H = log2(K) với K = số địa chỉ khác nhau | Số thực (bit) |
| **Phụ thuộc** | Địa chỉ main / buffer | Giá trị địa chỉ in ra | Hex (cho GĐ5, so sánh PIE) |

---

## 4. Yếu tố kiểm soát (controlled factors)

| Yếu tố | Cách kiểm soát |
|--------|-----------------|
| **Binary** | Cùng một nguồn (aslr_demo.c), cùng flags compile (-fno-stack-protector -z execstack); chỉ đổi -no-pie vs -fPIE -pie cho GĐ5. |
| **Môi trường** | Cùng OS (Ubuntu), kernel, kiến trúc (x86_64); ghi trong REPRODUCIBILITY (environment specification). |
| **Input** | Payload được tạo theo cùng công thức (exploit_config: OFFSET_RET, SHELLCODE); fixed addr trong GĐ2 lấy từ cùng máy khi ASLR=0. |
| **Số lần chạy** | GĐ2: N = 50 (hoặc tham số --runs); GĐ4: N = 500 (hoặc --runs). Cỡ mẫu đủ để ước lượng success rate và entropy. |

---

## 5. Cỡ mẫu (sample size)

| Thí nghiệm | N (số lần / số mẫu) | Lý do |
|------------|----------------------|--------|
| GĐ1 | 1 (hoặc vài lần kiểm chứng) | Chỉ cần chứng minh success khi ASLR=0; không cần thống kê. |
| GĐ2 | 50 (mặc định) | Đủ để ước lượng success rate; kỳ vọng 0% → 0/50. Có thể tăng (vd. 100) để tăng độ tin cậy. |
| GĐ3 | 1 (hoặc vài lần) | Chỉ cần chứng minh bypass thành công khi có leak. |
| GĐ4 | 500 (mặc định) | Đủ để ước lượng phân phối và entropy; có thể dùng bootstrap 95% CI (vd. --ci 500). |
| GĐ5 | 5 (hoặc vài lần mỗi binary) | Đủ để quan sát main cố định (non-PIE) vs thay đổi (PIE). |

---

## 6. Đo lường và chỉ số (metrics)

- **Success rate:** tỉ lệ lần chạy mà output có `uid=` (shell thành công). Dùng cho GĐ1, GĐ2, GĐ3 (xem EVALUATION_METRICS.md).
- **Entropy:** H_unique = log2(K), H_span = log2(span); tùy chọn 95% CI (bootstrap). Dùng cho GĐ4.
- **Số giá trị địa chỉ main khác nhau:** đếm unique(main_addr) cho non-PIE vs PIE. Dùng cho GĐ5.

---

## 7. Tóm tắt cho báo cáo

- **Thiết kế thí nghiệm** gồm: giả thuyết H1–H5, biến độc lập (ASLR, leak, PIE), biến phụ thuộc (success, entropy, địa chỉ), yếu tố kiểm soát (binary, môi trường, input), và cỡ mẫu (N) cho từng giai đoạn.
- **Reproducibility** đảm bảo qua tài liệu REPRODUCIBILITY.md và environment specification (phiên bản OS, kernel, compiler, Python).

*Tài liệu này bổ sung cho THREAT_MODEL.md, EVALUATION_METRICS.md và REPRODUCIBILITY.md.*
