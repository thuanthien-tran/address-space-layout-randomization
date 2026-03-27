# Threat Model — Đồ án ASLR

Tài liệu định nghĩa **mô hình mối đe dọa** (threat model) cho phạm vi đánh giá hiệu quả ASLR trong đồ án. Giúp báo cáo có **system-level context** và làm rõ phạm vi thực nghiệm.

---

## 1. Phạm vi (Scope)

| Thành phần | Mô tả |
|------------|--------|
| **Đối tượng đánh giá** | Cơ chế ASLR **userland** trên Linux (stack, heap, mmap, DSO). Không đánh giá kernel ASLR (KASLR). |
| **Lỗ hổng giả định** | Buffer overflow do đọc input không giới hạn (`gets()`), cho phép ghi đè return address trên stack. |
| **Mục tiêu tấn công** | Chiếm quyền thực thi (code execution): nhảy tới shellcode hoặc ROP. |
| **Lớp phòng thủ được đánh giá** | ASLR (randomize_va_space). Các lớp khác (canary, NX, PIE) được tắt hoặc bật có chủ đích để cô lập ảnh hưởng ASLR. |

---

## 2. Tài sản (Assets) và Mục tiêu

- **Tài sản:** Quyền thực thi mã tùy ý trong tiến trình (shell / arbitrary code).
- **Mục tiêu attacker:** Overwrite saved return address → redirect control flow → thực thi shellcode trên stack (trong đồ án: execve("/bin/sh")).

---

## 3. Giả định (Assumptions)

| Giả định | Mô tả |
|----------|--------|
| **A1** | Attacker có thể cung cấp input dài tùy ý vào chương trình (stdin). |
| **A2** | Attacker biết cấu trúc stack (offset từ buffer tới return address) — có thể reverse hoặc thử. |
| **A3** | Không có stack canary / NX trong bản demo để tập trung đánh giá ASLR; trong thực tế có thể có. |
| **A4** | Môi trường Linux x86-64; địa chỉ 8 byte, little-endian. |
| **A5 (GĐ3)** | Attacker có thể đọc được ít nhất một địa chỉ (information leak) — trong demo là chương trình in địa chỉ buffer ra stdout. |

---

## 4. Kịch bản tấn công (Attack scenarios)

| Kịch bản | Điều kiện | Hành động attacker | Kết quả đánh giá |
|----------|-----------|--------------------|-------------------|
| **S1 – Exploit khi ASLR OFF** | randomize_va_space=0 | Gửi payload: shellcode + padding + địa chỉ buffer (cố định). | **Thành công ổn định** → chứng minh lỗ hổng khai thác được. |
| **S2 – Exploit khi ASLR ON (fixed addr)** | randomize_va_space=2 | Dùng địa chỉ buffer lấy khi ASLR OFF, gửi cùng payload nhiều lần. | **Thất bại (0% hoặc rất thấp)** → chứng minh ASLR làm exploit không ổn định. |
| **S3 – Bypass bằng leak** | randomize_va_space=2 + có leak | Đọc địa chỉ buffer từ output, dùng làm return address trong payload. | **Thành công** → chứng minh info leak làm giảm hiệu quả ASLR. |

---

## 5. Đối tượng không nằm trong phạm vi

- **Kernel ASLR (KASLR):** Random hóa kernel image; cơ chế và entropy khác userland.
- **Full exploit chain:** Không mô phỏng ROP phức tạp, heap exploit, hay kết hợp nhiều lỗi.
- **Môi trường thực (hardening đầy đủ):** Production thường bật canary, NX, PIE; đồ án tắt một số để đánh giá riêng ASLR.

---

## 6. Tóm tắt cho báo cáo

*"Đồ án sử dụng threat model đơn giản: attacker có thể ghi đè return address qua buffer overflow và biết offset stack. Khi ASLR tắt (S1), exploit ổn định; khi ASLR bật (S2), exploit với địa chỉ cố định thất bại; khi có information leak (S3), attacker có thể bypass ASLR. Phạm vi đánh giá là ASLR userland trên Linux, không bao gồm KASLR hay full exploit chain."*

---

*Tài liệu này bổ sung cho README và ROADMAP; dùng khi viết phần "Mô hình đe dọa" hoặc "Phạm vi đánh giá" trong báo cáo.*
