# Makefile cho demo ASLR
# - aslr_demo: không PIE (dễ quan sát khi ASLR=0)
# - aslr_demo_pie: có PIE (so sánh địa chỉ main khi ASLR=2)

CC = gcc
CFLAGS = -fno-stack-protector -z execstack -no-pie -Wall
CFLAGS_PIE = -fno-stack-protector -z execstack -fPIE -pie -Wall
TARGET = aslr_demo
TARGET_PIE = aslr_demo_pie

.PHONY: all clean run run-off run-on check pie compare-pie

all: $(TARGET)

$(TARGET): aslr_demo.c
	$(CC) $(CFLAGS) aslr_demo.c -o $(TARGET) -ldl -ldl
	@echo "Build aslr_demo (no PIE). Chay: ./$(TARGET)"
	@echo "ASLR OFF: sudo sysctl -w kernel.randomize_va_space=0"
	@echo "ASLR ON:  sudo sysctl -w kernel.randomize_va_space=2"

# Bản có PIE - dùng để so sánh ASLR có PIE vs không PIE
$(TARGET_PIE): aslr_demo.c
	$(CC) $(CFLAGS_PIE) aslr_demo.c -o $(TARGET_PIE) -ldl
	@echo "Build aslr_demo_pie (PIE). Chay: ./$(TARGET_PIE)"
	@echo "Khi ASLR=2, dia chi main cung thay doi."

pie: $(TARGET_PIE)

# Build cả hai bản
both: $(TARGET) $(TARGET_PIE)
	@echo "Da build ca aslr_demo (no PIE) va aslr_demo_pie (PIE)."

clean:
	rm -f $(TARGET) $(TARGET_PIE)

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
