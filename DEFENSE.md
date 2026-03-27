# Phần Defense — ASLR và các lớp bảo vệ

## ASLR như một lớp phòng thủ

Trong đồ án này, **ASLR** đóng vai trò **defense** (phòng thủ):

- **GĐ1:** Khi ASLR **tắt** → exploit ổn định (attack thành công).
- **GĐ2:** Khi ASLR **bật** → dùng địa chỉ cố định → exploit **thất bại** (crash, 0% success).  
  → **ASLR có hiệu quả** trong việc làm exploit không ổn định.
- **GĐ3:** Khi có **information leak** (chương trình in địa chỉ) → attacker vẫn có thể bypass.  
  → ASLR **không đủ một mình**; cần tránh leak và kết hợp các cơ chế khác.

## Khuyến nghị phòng thủ (defense in depth)

| Lớp | Mô tả |
|-----|--------|
| **Sửa lỗi** | Không dùng `gets()`, dùng hàm an toàn (vd. `fgets`), kiểm tra biên. |
| **ASLR** | Bật `randomize_va_space=2` (đã demo hiệu quả trong GĐ2). |
| **PIE** | Compile với `-fPIE -pie` để random luôn vùng code (GĐ5). |
| **Stack canary** | Không tắt trong production (`-fno-stack-protector` chỉ cho demo). |
| **DEP/NX** | Không cho phép thực thi trên stack (`-z execstack` chỉ cho demo). |
| **Giảm info leak** | Tránh in con trỏ/địa chỉ ra log hoặc cho user (tránh bypass như GĐ3). |

**Kết luận ngắn:** ASLR là một lớp phòng thủ quan trọng và đã được chứng minh qua thực nghiệm (GĐ2); để bảo vệ tốt hơn cần kết hợp sửa lỗi, PIE, canary, DEP và hạn chế information leak.

---

## Bối cảnh hệ thống (system-level context)

- **Userland vs kernel:** Đồ án đánh giá ASLR **trong không gian user** (tiến trình). Kernel có cơ chế riêng (KASLR) — random hóa kernel image khi boot; không nằm trong phạm vi đo của đồ án.
- **Vai trò kernel:** Kernel cung cấp entropy (random offsets) khi tạo tiến trình (stack) và khi loader map thư viện/heap; `randomize_va_space` bật/tắt mức độ random này.
- **Vai trò loader (ld.so):** Dynamic linker map DSO (libc, ld) vào vùng địa chỉ đã được kernel/linker random; kết quả là địa chỉ printf (libc) thay đổi khi ASLR bật (đã quan sát trong demo).

---

## Modern mitigations (bổ sung cho báo cáo)

Ngoài ASLR, stack canary, DEP/NX và PIE, các cơ chế **hiện đại** thường được nhắc trong tài liệu an ninh (đồ án không thực nghiệm, chỉ nêu để mở rộng):

| Mitigation | Mô tả ngắn |
|-------------|------------|
| **CFI (Control Flow Integrity)** | Giới hạn luồng điều khiển hợp lệ (chỉ cho phép nhảy tới các đích đã định) → khó chuyển control flow tùy ý. |
| **SafeStack** | Tách biến nhạy cảm (vd. con trỏ) sang stack riêng → giảm rủi ro overwrite. |
| **Shadow Stack** | Stack bóng lưu bản sao return address → kiểm tra khi return. |
| **CET (Intel)** | Phần cứng hỗ trợ shadow stack / indirect branch tracking. |

**Câu nói gợi ý:** *"ASLR là nền tảng; trong thực tế hệ thống thường kết hợp thêm CFI, SafeStack, và các cơ chế phần cứng (CET) để tăng chi phí tấn công."*
