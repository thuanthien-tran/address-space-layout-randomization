#!/bin/bash
# Script demo ASLR - chạy trên Ubuntu/Linux
# Cách dùng:
#   ./demo_commands.sh           - demo tương tác (có nhắc Enter)
#   ./demo_commands.sh --log     - demo và lưu toàn bộ output vào demo_log.txt (để minh họa báo cáo)

LOG_FILE="demo_log.txt"
DO_LOG=""

if [ "$1" = "--log" ] || [ "$1" = "-l" ]; then
    DO_LOG="yes"
    : > "$LOG_FILE"
    echo "Che do ghi log: ket qua se luu vao $LOG_FILE"
    echo "Luu y: Ban can tat/bat ASLR truoc (sudo sysctl -w kernel.randomize_va_space=0 hoac 2)."
    exec 1> >(tee -a "$LOG_FILE")
fi

run_demo() {
    echo "AAAA" | ./aslr_demo 2>/dev/null || true
}

set -e
echo "=== Kiem tra trang thai ASLR ==="
echo "Gia tri hien tai: $(cat /proc/sys/kernel/randomize_va_space) (0=OFF, 2=ON)"
echo ""

if [ ! -f ./aslr_demo ]; then
    echo "Chua co file aslr_demo. Dang compile..."
    make -f Makefile aslr_demo 2>/dev/null || gcc aslr_demo.c -fno-stack-protector -z execstack -no-pie -o aslr_demo
fi

echo "=== DEMO 1: ASLR TAT (dia chi co dinh) ==="
echo "Lenh: sudo sysctl -w kernel.randomize_va_space=0"
if [ -z "$DO_LOG" ]; then
    read -p "Nhan Enter sau khi da tat ASLR (hoac chay lenh tren)..."
fi

echo "Chay 3 lan - quan sat dia chi giong nhau:"
for i in 1 2 3; do
    echo "--- Lan $i ---"
    run_demo
done

echo ""
echo "=== DEMO 2: ASLR BAT (dia chi thay doi) ==="
echo "Lenh: sudo sysctl -w kernel.randomize_va_space=2"
if [ -z "$DO_LOG" ]; then
    read -p "Nhan Enter sau khi da bat ASLR (hoac chay lenh tren)..."
fi

echo "Chay 3 lan - quan sat dia chi khac nhau:"
for i in 1 2 3; do
    echo "--- Lan $i ---"
    run_demo
done

echo ""
echo "=== KET THUC DEMO ==="
echo "Ket luan: ASLR OFF -> dia chi co dinh; ASLR ON -> dia chi random."

if [ -n "$DO_LOG" ]; then
    echo ""
    echo "Da ghi log vao: $LOG_FILE (co the dung de chen vao bao cao/slide)."
fi
