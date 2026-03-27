# Tài liệu tham khảo – Đồ án ASLR

Dùng để trích dẫn trong báo cáo và thể hiện nghiên cứu sâu.

## Tài liệu chính

1. **Linux kernel – ASLR**  
   - `Documentation/admin-guide/sysctl/kernel.rst` (randomize_va_space)  
   - Nguồn: https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html  

2. **Address Space Layout Randomization (ASLR)**  
   - PaX Team, 2003 – khái niệm và triển khai ban đầu.  
   - Có thể tìm: "PaX ASLR" hoặc "Address space layout randomization" trên scholar.

3. **Linux man pages**  
   - `man 2 personality` (ADDR_NO_RANDOMIZE)  
   - `man 7 elf` (PIE, dynamic linker)

4. **Sách / slide an ninh hệ điều hành**  
   - "Computer Security: Principles and Practice" – Stallings (phần OS security).  
   - Slide môn An toàn Hệ điều hành (trường bạn).

## Trích dẫn gợi ý cho báo cáo

- *"ASLR là kỹ thuật random hóa không gian địa chỉ (stack, heap, thư viện, executable) nhằm làm khó việc đoán địa chỉ trong khai thác memory corruption."*
- *"Trên Linux, mức randomize_va_space điều khiển phạm vi ASLR; giá trị 2 tương ứng với random hóa đầy đủ."*
- *"ASLR không sửa lỗi lập trình (ví dụ buffer overflow) mà là lớp phòng thủ bổ sung (defense in depth)."*

## Ghi chú

- Nếu thầy yêu cầu danh mục tài liệu chuẩn (IEEE/APA), chỉnh lại định dạng trích dẫn từ các nguồn trên.
