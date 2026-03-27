# System-Level Depth — KASLR, kiến trúc, loader

Tài liệu bổ sung **độ sâu hệ thống** cho báo cáo: so sánh Kernel ASLR với userland, khác biệt entropy theo kiến trúc, và cơ chế mapping của loader. Giúp thể hiện hiểu bản chất ở mức OS/system.

---

## 1. Kernel ASLR (KASLR) — Discussion

### 1.1 Khác biệt với userland ASLR

| Khía cạnh | Userland ASLR (đồ án đánh giá) | Kernel ASLR (KASLR) |
|-----------|--------------------------------|---------------------|
| **Đối tượng** | Stack, heap, mmap, DSO, PIE executable của **tiến trình user**. | **Kernel image**, kernel modules, một số cấu trúc nội bộ kernel. |
| **Thời điểm random** | Mỗi lần **tạo tiến trình** hoặc **map vùng nhớ** (mmap, load DSO). | Thường **một lần khi boot** (trước khi userland chạy). |
| **Điều khiển** | `randomize_va_space` (0/1/2) — áp dụng cho tiến trình. | Tham số kernel boot (vd. `kaslr` trên Linux), hoặc mặc định bật tùy distro. |
| **Entropy** | Stack/heap/lib: cỡ ~16–30 bit tùy kernel và kiến trúc; **thay đổi mỗi process**. | Kernel base: cỡ ~24–30 bit (tùy kiến trúc); **cố định sau boot** cho đến khi reboot. |
| **Mục đích** | Ngăn đoán địa chỉ trong **exploit user process** (buffer overflow, ROP trong user space). | Ngăn đoán địa chỉ kernel khi attacker đã có khả năng đọc/ghi kernel (vd. từ user exploit hoặc module). |

### 1.2 Vì sao đồ án không đo KASLR

- Đồ án tập trung **buffer overflow trong user process** → địa chỉ cần đoán là **stack/user heap**, không phải kernel.
- Đo KASLR cần đọc `/proc/kallsyms` hoặc tương đương (thường cần quyền); và entropy kernel **không đổi** trong một phiên boot → không có “phân phối” nhiều lần chạy như user stack.
- Nêu **phân biệt** userland vs KASLR trong báo cáo cho thấy hiểu **system-level**: có hai lớp ASLR khác nhau (process-level vs kernel-level).

**Câu nói gợi ý:** *"ASLR trong đồ án là userland ASLR. Kernel ASLR (KASLR) random hóa địa chỉ kernel khi boot, có cơ chế và entropy riêng; không nằm trong phạm vi đo của đồ án nhưng là phần bổ trợ quan trọng cho an ninh hệ thống."*

---

## 2. Architecture entropy difference

Entropy (số bit ngẫu nhiên) **phụ thuộc kiến trúc** và kernel:

### 2.1 So sánh theo kiến trúc (ước lượng, Linux)

| Kiến trúc | Không gian địa chỉ | Stack / mmap entropy (ước lượng) | Ghi chú |
|-----------|--------------------|-----------------------------------|--------|
| **x86 32-bit** | 32 bit | ~12–16 bit | Không gian hẹp; số bit random thường thấp hơn 64-bit. |
| **x86-64 (amd64)** | 64 bit | ~19–30 bit | Đồ án đo trên kiến trúc này. |
| **ARM / ARM64** | 32 / 64 bit | Khác x86; phụ thuộc kernel ARM | Một số thiết bị entropy thấp (vd. embedded). |

### 2.2 Giải thích ngắn

- **32-bit:** Địa chỉ chỉ 4 byte; kernel thường dành một phần cho random (vd. stack top) → entropy bị giới hạn bởi không gian và alignment.
- **64-bit:** Không gian địa chỉ rất lớn → kernel có thể random nhiều bit hơn mà vẫn nằm trong vùng hợp lệ (vd. user half của address space).
- **Kernel version:** Cơ chế random (vd. `arch_get_unmapped_area` trên Linux) có thể thay đổi giữa các phiên bản → entropy thực tế phụ thuộc môi trường.

**Ý nghĩa với đồ án:** Kết quả entropy (GĐ4) là **trên x86-64, kernel cụ thể**; trên kiến trúc hoặc kernel khác, số bit có thể khác. Đây là **architecture-dependent** và nên nêu trong báo cáo.

---

## 3. Loader mapping mechanism (tóm tắt)

Địa chỉ thư viện (vd. `printf` trong libc) và PIE executable **không do chương trình user quyết định** mà do **loader (dynamic linker)** và **kernel** phối hợp.

### 3.1 Luồng tổng quát

1. **Kernel tạo process:** Khi `execve()`, kernel load ELF; đọc `randomize_va_space`. Nếu ASLR bật, kernel (hoặc loader trong user space) yêu cầu **random base** cho vùng map.
2. **Vùng stack:** Kernel (vd. trong `load_elf_binary` hoặc khi setup stack) đặt stack top ở địa chỉ **random** (trong vùng user); stack base của process phụ thuộc giá trị này.
3. **Vùng heap / mmap:** Khi process gọi `malloc` (sbrk/mmap) hoặc `mmap()`, kernel chọn địa chỉ qua **mmap handler**; trên Linux thường gọi tới `arch_get_unmapped_area()` (hoặc tương đương) — hàm này có thể **cộng thêm offset ngẫu nhiên** (random_offset) trong vùng cho phép.
4. **DSO (thư viện):** Dynamic linker (`ld.so`) load các thư viện (libc, …). Với mỗi DSO, linker gọi **mmap** để map file vào bộ nhớ; địa chỉ base do kernel (hoặc linker với kernel hỗ trợ) chọn — **có random** khi ASLR bật → địa chỉ `printf` (trong libc) thay đổi mỗi lần chạy.
5. **PIE executable:** Binary PIE được map tương tự DSO: base của chính file thực thi cũng **random** → địa chỉ `main` thay đổi.

### 3.2 Điểm then chốt (cho báo cáo)

- **Kernel** cung cấp cơ chế chọn địa chỉ có random (vd. `arch_get_unmapped_area`, stack randomization).
- **Loader (ld.so)** không “tự nghĩ ra” địa chỉ; nó yêu cầu map tại vùng địa chỉ, kernel (hoặc cơ chế do kernel cung cấp) trả về địa chỉ **đã được random**.
- Kết quả quan sát trong demo (địa chỉ main, printf, buffer, heap thay đổi khi ASLR=2) là **hệ quả** của cơ chế mapping này ở mức hệ điều hành.

**Câu nói gợi ý:** *"Địa chỉ stack, heap và thư viện được random thông qua cơ chế mapping của kernel và loader (vd. arch_get_unmapped_area, dynamic linker); đồ án quan sát kết quả ở user space và đo entropy stack, không đi sâu mã nguồn kernel."*

---

## 4. Tóm tắt cho báo cáo (system-level depth)

- **KASLR vs userland:** Userland ASLR áp dụng cho từng process; KASLR cho kernel khi boot — hai lớp độc lập, đồ án đánh giá userland.
- **Architecture entropy:** Entropy phụ thuộc kiến trúc (32-bit thường thấp hơn 64-bit) và kernel; kết quả GĐ4 đúng cho môi trường x86-64 đã dùng.
- **Loader mechanism:** Địa chỉ stack/heap/DSO là kết quả của kernel (randomized mapping) và loader (map DSO, PIE); nêu ngắn cơ chế này thể hiện độ sâu system-level.

*Tài liệu này bổ sung cho LY_THUYET_VA_MO_RONG.md và DEFENSE.md; dùng khi viết phần "Bối cảnh hệ thống" hoặc "Độ sâu hệ điều hành" trong báo cáo.*
