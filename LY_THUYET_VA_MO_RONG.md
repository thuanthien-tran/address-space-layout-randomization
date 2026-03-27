# Lý thuyết mở rộng – ASLR (Entropy, hạn chế, PIE, thực tế)

Tài liệu bổ sung cho báo cáo đồ án: entropy, hạn chế của ASLR, so sánh PIE, liên hệ thực tế và sơ đồ layout bộ nhớ.

---

## 1. Entropy của ASLR (độ ngẫu nhiên)

### 1.1 Vì sao cần phân tích entropy?

Demo chứng minh *địa chỉ thay đổi* khi bật ASLR. Để giải thích *vì sao* exploit trở nên kém ổn định, cần nói đến **entropy** (số bit ngẫu nhiên): càng nhiều bit, không gian địa chỉ càng khó đoán.

### 1.2 Entropy theo từng vùng (Linux, mức 2)

| Vùng | Entropy ước lượng (bit) | Ghi chú |
|------|-------------------------|--------|
| **Stack** | ~19–30 bit | Offset stack base ngẫu nhiên |
| **Heap / mmap** | ~16–28 bit | Vùng cấp phát động |
| **Thư viện (libc, ld)** | ~16–24 bit | Base của DSO thay đổi |
| **Executable (khi có PIE)** | ~16–24 bit | Base của ELF thay đổi |

*(Giá trị cụ thể phụ thuộc kernel và kiến trúc; bảng mang tính ước lượng.)*

### 1.3 Xác suất đoán trúng địa chỉ

Nếu kẻ tấn công cần đoán **một** địa chỉ có **n** bit entropy:

- **Xác suất đoán trúng một lần** ≈ \( \frac{1}{2^n} \)
- Ví dụ: 20 bit entropy → \( \frac{1}{2^{20}} \approx \frac{1}{1\,000\,000} \)

**Ý nghĩa khi báo cáo:**  
*"ASLR không chỉ làm địa chỉ thay đổi; entropy khiến xác suất đoán trúng rất thấp, nên exploit dựa trên địa chỉ cố định trở nên không ổn định và khó tái sử dụng."*

---

## 2. Hạn chế của ASLR (rất nên có trong báo cáo)

ASLR là **một lớp phòng thủ**, không phải giải pháp toàn năng. Nên nêu rõ:

| Hạn chế | Giải thích ngắn |
|--------|------------------|
| **Không vá lỗi** | Không sửa buffer overflow hay lỗi lập trình; chỉ làm khai thác khó hơn. |
| **Information leak** | Nếu có lỗi leak địa chỉ (printf, crash dump…), attacker có thể biết base → bypass ASLR. |
| **Bypass bằng ROP** | Nếu leak được địa chỉ thư viện (vd. libc), có thể dùng ROP với địa chỉ thật. |
| **Entropy hữu hạn** | Trên một số hệ thống entropy thấp hoặc có thể brute-force (vd. fork không re-random). |
| **Không bảo vệ dữ liệu** | ASLR bảo vệ layout, không mã hóa hay bảo vệ nội dung bộ nhớ. |

**Câu kết:**  
*"ASLR tăng chi phí tấn công và giảm tính ổn định của exploit, nhưng cần kết hợp với sửa lỗi, DEP, stack canary, PIE và giảm info leak."*

---

## 3. So sánh ASLR có PIE và không PIE

### 3.1 Khái niệm

- **PIE (Position Independent Executable):** executable được biên dịch để có thể load ở địa chỉ bất kỳ; khi ASLR bật, địa chỉ **main** (và toàn bộ code) thay đổi mỗi lần chạy.
- **Không PIE (-no-pie):** địa chỉ code (main, hàm) **cố định**; chỉ stack/heap/lib thay đổi khi ASLR bật.

### 3.2 Bảng so sánh (dùng trong báo cáo)

| Tiêu chí | ASLR ON + **không** PIE | ASLR ON + **có** PIE |
|----------|-------------------------|------------------------|
| Địa chỉ **main** (code) | Cố định | Thay đổi mỗi lần chạy |
| Địa chỉ stack (buffer) | Thay đổi | Thay đổi |
| Địa chỉ thư viện (printf…) | Thay đổi | Thay đổi |
| Khai thác ROP/JOP | Có thể dùng gadget trong executable (địa chỉ cố định) | Executable cũng random → khó hơn |
| **Vai trò PIE** | Chỉ random stack/heap/lib | Random **toàn bộ** không gian địa chỉ (gồm code) |

**Kết luận:**  
PIE bổ sung cho ASLR bằng cách random hóa luôn vùng code, tăng entropy và giảm khả năng lợi dụng gadget cố định trong binary.

### 3.3 Cách demo trong project

- Build **không PIE:** `make` → `aslr_demo` (địa chỉ main cố định khi ASLR=0).
- Build **có PIE:** `make pie` → `aslr_demo_pie` (địa chỉ main thay đổi khi ASLR=2).
- Chạy cả hai với ASLR=2, so sánh địa chỉ main trong bảng (xem **demo_aslr/README_DEMO.md**).

---

## 4. Sơ đồ layout bộ nhớ (trước / sau ASLR)

### 4.1 Khi ASLR tắt (layout cố định)

```
Địa chỉ cao
+------------------+
|       Stack      |  ← buffer, frame, return address (cố định)
+------------------+
|        ...       |
+------------------+
|   Heap / mmap    |  ← malloc (cố định)
+------------------+
|   Thư viện       |  ← libc, ld (cố định)
+------------------+
|   Executable     |  ← main, code (cố định nếu không PIE)
+------------------+
Địa chỉ thấp
```

### 4.2 Khi ASLR bật (layout random)

```
Địa chỉ cao
+------------------+
|       Stack      |  ← offset ngẫu nhiên mỗi lần chạy
+------------------+
|        ...       |
+------------------+
|   Heap / mmap    |  ← base ngẫu nhiên
+------------------+
|   Thư viện       |  ← base ngẫu nhiên
+------------------+
|   Executable     |  ← base ngẫu nhiên (nếu PIE)
+------------------+
Địa chỉ thấp
```

**Ghi chú:** Vị trí **tương đối** giữa các vùng có thể giữ; **base** (địa chỉ bắt đầu) của stack, heap, lib, executable thay đổi theo ASLR (và PIE).

---

## 5. Liên hệ thực tế & hệ điều hành khác

### 5.1 Windows

- ASLR có từ Windows Vista; cùng với **DEP** (Data Execution Prevention).
- Random hóa: image (exe/dll), stack, heap, PEB/TEB.
- Có thể tắt cho từng process (vd. compatibility).

### 5.2 Android

- ASLR (và PIE cho app) được dùng từ các phiên bản Android sau; app 64-bit thường bắt buộc PIE.
- Kết hợp với SELinux, sandbox.

### 5.3 Một số CVE liên quan bypass ASLR (chỉ mô tả)

- **Information leak + ROP:** Nhiều CVE khai thác lỗi leak địa chỉ (vd. format string, out-of-bound read) để lấy base libc/executable, sau đó ROP. ASLR không ngăn được nếu đã leak.
- **Brute-force / spray:** Trên môi trường entropy thấp hoặc fork không re-random (đã được sửa/cải thiện ở nhiều OS), từng có nghiên cứu brute-force địa chỉ.
- **Side-channel:** Một số nghiên cứu dùng timing/side-channel để suy đoán layout (phức tạp, thường cần điều kiện đặc biệt).

*Trong báo cáo chỉ cần nêu ngắn: "ASLR có thể bị bypass khi kết hợp info leak hoặc trong điều kiện đặc biệt; nhiều CVE đã khai thác điều này."*

---

## 5.4 Bối cảnh hệ thống: Userland ASLR vs Kernel ASLR (KASLR)

Đồ án đánh giá **userland ASLR** (stack, heap, thư viện, executable khi PIE). Cần phân biệt với **KASLR**:

| Loại | Phạm vi | Cơ chế (tóm tắt) | Đồ án có đánh giá? |
|------|---------|-------------------|---------------------|
| **Userland ASLR** | Tiến trình user: stack, heap, mmap, DSO, (PIE) executable | Kernel cung cấp random offset khi load ELF, map stack/heap; `randomize_va_space` điều khiển. | **Có** — toàn bộ thực nghiệm. |
| **KASLR** | Kernel image, module | Random offset khi boot; entropy và cơ chế khác userland. | **Không** — ngoài phạm vi. |

**Entropy phụ thuộc kiến trúc:** Trên x86-64 Linux, số bit random cho stack/heap/lib có thể khác giữa kernel version và kiến trúc (vd. 32-bit thường ít bit hơn 64-bit). Script entropy trong đồ án đo **trên môi trường cụ thể** (x86-64, kernel hiện tại).

**Cơ chế mmap / loader (tóm tắt):** Thư viện và vùng mmap được loader (ld.so) map với base address lấy từ kernel (random); stack base cũng do kernel random khi tạo tiến trình. Chi tiết nằm trong kernel (vd. `arch_get_unmapped_area`) và dynamic linker; đồ án không đi sâu implementation mà chỉ quan sát kết quả (địa chỉ thay đổi).

---

## 6. Bảng tổng kết kết quả demo (mẫu)

Điền sau khi chạy demo trên Linux (ASLR=0 và ASLR=2). Dùng cho báo cáo hoặc slide.

### 6.1 Phiên bản không PIE (aslr_demo)

| Lần chạy | ASLR=0 – main | ASLR=0 – buffer | ASLR=2 – main | ASLR=2 – buffer |
|----------|----------------|-----------------|---------------|-----------------|
| 1        | (điền)         | (điền)          | (điền)        | (điền)          |
| 2        | (điền)         | (điền)          | (điền)        | (điền)          |
| 3        | (điền)         | (điền)          | (điền)        | (điền)          |
| **Nhận xét** | Giống nhau   | Giống nhau      | Khác nhau     | Khác nhau       |

*(Có thể thêm cột: printf, heap nếu dùng bản demo mở rộng.)*

### 6.2 Phiên bản có PIE (aslr_demo_pie) – khi ASLR=2

| Lần chạy | main (PIE) | buffer |
|----------|------------|--------|
| 1        | (điền)     | (điền) |
| 2        | (điền)     | (điền) |
| 3        | (điền)     | (điền) |

**Nhận xét:** Địa chỉ main cũng thay đổi khi có PIE + ASLR.

---

*Tài liệu này bổ sung cho ROADMAP_ASLR.md và TAI_LIEU_THAM_KHAO.md; dùng khi viết báo cáo và slide.*
