# Demo ASLR – Hướng dẫn nhanh

## Mục tiêu

Chứng minh ASLR làm thay đổi layout bộ nhớ tiến trình (executable, stack, heap, thư viện) và khiến khai thác buffer overflow khó hơn.

## Yêu cầu

- Ubuntu Linux (hoặc VM)
- `gcc` (build-essential)

## Địa chỉ in ra khi chạy chương trình

Chương trình in **bốn** loại địa chỉ để quan sát ASLR toàn diện:

| Địa chỉ    | Vùng        | Ý nghĩa                          |
|------------|-------------|-----------------------------------|
| main       | executable  | Code chương trình                 |
| printf     | library     | Hàm thư viện (libc)               |
| buffer     | stack       | Biến cục bộ trong hàm             |
| heap       | heap/malloc | Vùng cấp phát động (malloc)       |

→ ASLR khi bật sẽ làm **cả bốn** thay đổi (trừ main nếu compile không PIE khi ASLR=0).

## Các bước thực hiện

### 1. Kiểm tra ASLR

```bash
cat /proc/sys/kernel/randomize_va_space
# 0 = OFF, 2 = ON (full)
```

### 2. Compile

```bash
make
# Tạo aslr_demo (không PIE). Hoặc:
# gcc aslr_demo.c -fno-stack-protector -z execstack -no-pie -o aslr_demo
```

**So sánh PIE vs không PIE (tùy chọn):**

```bash
make pie          # tạo aslr_demo_pie (có PIE)
make compare-pie  # chạy cả hai khi ASLR=2, in ra để điền bảng
```

### 3. Demo ASLR tắt

```bash
sudo sysctl -w kernel.randomize_va_space=0
./aslr_demo
./aslr_demo
./aslr_demo
```

→ Các địa chỉ **giống nhau** mỗi lần.

### 4. Demo ASLR bật

```bash
sudo sysctl -w kernel.randomize_va_space=2
./aslr_demo
./aslr_demo
./aslr_demo
```

→ Các địa chỉ **thay đổi** mỗi lần chạy.

### 5. Lưu log để minh họa báo cáo

```bash
cd demo_aslr
./demo_commands.sh --log
```

Output vừa hiện trên màn hình vừa được ghi vào `demo_log.txt`. Chạy lần 1 với ASLR=0, lần 2 với ASLR=2 (nhớ đổi sysctl trước mỗi lần) rồi gộp hoặc giữ hai file log để đưa vào báo cáo/slide.

### 6. Kết luận khi báo cáo

- ASLR random hóa không gian địa chỉ (stack, heap, lib, và executable nếu PIE).
- ASLR tắt → địa chỉ cố định → dễ khai thác.
- ASLR bật → địa chỉ thay đổi → exploit khó thành công.
- ASLR là một lớp phòng thủ, không thay thế việc sửa lỗi.

## Lỗi thường gặp

- **Quên `-no-pie`** (khi build bản so sánh) → địa chỉ main vẫn đổi khi ASLR=0 → dùng đúng target trong Makefile.
- **Quên bật/tắt ASLR** → kiểm tra bằng `cat /proc/sys/kernel/randomize_va_space` trước mỗi phần demo.

Chi tiết đầy đủ: **ROADMAP_ASLR.md** và **LY_THUYET_VA_MO_RONG.md** ở thư mục gốc project.
