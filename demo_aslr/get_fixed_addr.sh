#!/bin/bash
# Lấy địa chỉ buffer cố định khi ASLR TẮT — dùng cho Giai đoạn 2 (exploit fail khi ASLR ON).
# Chạy: ./get_fixed_addr.sh
# Sau đó: sudo sysctl -w kernel.randomize_va_space=2
#         python3 ../exploits/exploit_phase2_aslr_on_fail.py --fixed-addr <địa chỉ in ra>
#
# Nếu lỗi "bad interpreter: /bin/bash^M": file có CRLF (Windows). Sửa trên Kali:
#   sed -i 's/\r$//' get_fixed_addr.sh && chmod +x get_fixed_addr.sh

echo "Đảm bảo ASLR đang TẮT: kernel.randomize_va_space=0"
echo "Gia tri hien tai: $(cat /proc/sys/kernel/randomize_va_space)"
echo ""
echo "Dia chi buffer (copy vao --fixed-addr):"
echo "AAAA" | ./aslr_demo 2>/dev/null | grep -i buffer
