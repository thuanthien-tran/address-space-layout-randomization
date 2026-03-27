# Makefile cho demo ASLR
# - aslr_demo: không PIE (dễ quan sát khi ASLR=0)
# - aslr_demo_pie: có PIE (so sánh địa chỉ main khi ASLR=2)

CC = gcc
# Bản demo shellcode (stack executable) - chỉ dùng cho phase 1-3
CFLAGS = -fno-stack-protector -z execstack -no-pie -Wall
CFLAGS_PIE = -fno-stack-protector -z execstack -fPIE -pie -Wall
# Bản NX ON (noexecstack) - dùng cho ROP phase 4
CFLAGS_NX = -fno-stack-protector -z noexecstack -no-pie -Wall
CFLAGS_NX_PIE = -fno-stack-protector -z noexecstack -fPIE -pie -Wall
# Tùy chọn canary để so sánh mitigation stack protector
CFLAGS_NX_CANARY = -fstack-protector-strong -z noexecstack -no-pie -Wall
TARGET = aslr_demo
TARGET_PIE = aslr_demo_pie
TARGET_NX = aslr_demo_nx
TARGET_NX_PIE = aslr_demo_nx_pie
TARGET_NX_CANARY = aslr_demo_nx_canary

.PHONY: all clean run run-off run-on check pie nx nx-pie nx-canary both compare-pie

all: $(TARGET)

$(TARGET): aslr_demo.c
	$(CC) $(CFLAGS) aslr_demo.c -o $(TARGET)
	@echo "Build aslr_demo (no PIE). Chay: ./$(TARGET)"
	@echo "ASLR OFF: sudo sysctl -w kernel.randomize_va_space=0"
	@echo "ASLR ON:  sudo sysctl -w kernel.randomize_va_space=2"

# Bản có PIE - dùng để so sánh ASLR có PIE vs không PIE
$(TARGET_PIE): aslr_demo.c
	$(CC) $(CFLAGS_PIE) aslr_demo.c -o $(TARGET_PIE)
	@echo "Build aslr_demo_pie (PIE). Chay: ./$(TARGET_PIE)"
	@echo "Khi ASLR=2, dia chi main cung thay doi."

pie: $(TARGET_PIE)

# Bản NX ON (noexecstack) - dùng cho ROP demo
$(TARGET_NX): aslr_demo.c
	$(CC) $(CFLAGS_NX) aslr_demo.c -o $(TARGET_NX)
	@echo "Build aslr_demo_nx (NX ON, no PIE). Chay: ./$(TARGET_NX)"
	@echo "Dùng cho ROP phase 4: python3 ../exploits/exploit_phase4_rop.py"

# Bản NX ON + PIE
$(TARGET_NX_PIE): aslr_demo.c
	$(CC) $(CFLAGS_NX_PIE) aslr_demo.c -o $(TARGET_NX_PIE)
	@echo "Build aslr_demo_nx_pie (NX ON + PIE)."

# Bản NX ON + stack canary
$(TARGET_NX_CANARY): aslr_demo.c
	$(CC) $(CFLAGS_NX_CANARY) aslr_demo.c -o $(TARGET_NX_CANARY)
	@echo "Build aslr_demo_nx_canary (NX ON + Canary)."

nx: $(TARGET_NX)
nx-pie: $(TARGET_NX_PIE)
nx-canary: $(TARGET_NX_CANARY)

# Build cả hai bản
both: $(TARGET) $(TARGET_PIE) $(TARGET_NX)
	@echo "Da build aslr_demo, aslr_demo_pie, aslr_demo_nx."

clean:
	rm -f $(TARGET) $(TARGET_PIE) $(TARGET_NX) $(TARGET_NX_PIE) $(TARGET_NX_CANARY)

# Chạy demo (giữ nguyên cài đặt ASLR hiện tại)
run: $(TARGET)
	./$(TARGET)

# In trạng thái ASLR hiện tại
check:
	@echo "Trang thai ASLR: $$(cat /proc/sys/kernel/randomize_va_space) (0=OFF, 2=ON)"

# Gợi ý: tắt ASLR rồi chạy 3 lần (cần quyền sudo để set)
run-off: check
	@echo "Tat ASLR (can sudo): sysctl -w kernel.randomize_va_space=0"
	@echo "Sau do chay: ./$(TARGET) (nhieu lan de so sanh dia chi)"

# Gợi ý: bật ASLR rồi chạy 3 lần
run-on: check
	@echo "Bat ASLR (can sudo): sysctl -w kernel.randomize_va_space=2"
	@echo "Sau do chay: ./$(TARGET) (nhieu lan de so sanh dia chi)"

# So sánh PIE vs no-PIE: chạy cả hai khi ASLR=2, in ra để điền bảng
compare-pie: $(TARGET) $(TARGET_PIE)
	@echo "=== So sanh PIE vs no-PIE (can ASLR=2) ==="
	@echo "Chay: sudo sysctl -w kernel.randomize_va_space=2"
	@echo ""
	@echo "--- aslr_demo (NO PIE) ---"
	@echo "AAAA" | ./$(TARGET) 2>/dev/null || true
	@echo ""
	@echo "--- aslr_demo_pie (PIE) ---"
	@echo "AAAA" | ./$(TARGET_PIE) 2>/dev/null || true
	@echo "Dien ket qua vao bang trong LY_THUYET_VA_MO_RONG.md (muc 6.2)"
