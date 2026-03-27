# Hardcoded Assumptions & Limitations — Đồ án ASLR

Tài liệu **chỉ rõ** các giả định nguy hiểm và hạn chế của exploit/entropy trong đồ án. Giúp giảng viên thấy: đây là **demo / evaluation study**, không phải generalizable production exploit; và các giả định học thuật được nêu tường minh.

---

## 1. Hardcoded / assumption nguy hiểm (exploit)

### 1.1 OFFSET / ADDRESS ASSUMPTION

**Nơi:** `exploit_config.py`, `exploit_phase1_aslr_off.py`, `exploit_phase3_bypass_leak.py`

**Giả định:**  
- `ret_addr = buffer_addr + 0` (return address = địa chỉ buffer, không offset).  
- Offset từ buffer tới saved RIP = **72 byte cố định** (buffer 64 + saved RBP 8).

**Chỉ đúng khi:**
- Cùng **compiler** và **flags** (không đổi optimization, layout).
- Cùng **ABI / calling convention** (x86-64).
- Không có canary, không thay đổi frame layout.

**Chưa xử lý:** Khác libc version, kernel, ASLR entropy config, stack alignment khác → offset/address có thể sai. **Đây là demo exploit assumption, không phải generalizable analysis.**

---

### 1.2 SINGLE-RUN / DETERMINISM ASSUMPTION

**Vấn đề:** Nếu chỉ chạy exploit **1 lần** success → kết luận "OK" thì đang assume **determinism**. Trong khi ASLR là **probabilistic mitigation** → cần **đo success probability** (chạy N lần, success rate), không chỉ success/fail đơn lẻ.

**Cách đồ án xử lý:** Script **exploit_success_probability.py** chạy 500 lần khi ASLR OFF và 500 lần khi ASLR ON (fixed addr), báo cáo **success rate** và so sánh: *"ASLR reduces exploit success probability from X% to Y%".* → Phù hợp mitigation evaluation chuẩn research.

---

### 1.3 ENVIRONMENT CONSTANT

**Giả định ngầm:** ASLR entropy, mmap behavior, stack random range là **cố định** trong suốt thí nghiệm.

**Thực tế ảnh hưởng:**  
- `kernel.randomize_va_space` (0/1/2)  
- `ulimit -s` (stack size)  
- PIE flag (binary)  
- Loader / ld.so version  

**Đồ án:** Ghi rõ trong REPRODUCIBILITY (environment specification); không formalize biến môi trường thành tham số thí nghiệm. **Hạn chế có ý thức.**

---

### 1.4 LEAK RELIABILITY

**Giả định (bypass GĐ3):** Leak địa chỉ buffer **luôn đúng**, không noise, không partial leak.

**Thực tế:** Leak có thể có variance, alignment, lazy binding → địa chỉ đọc được có thể lệch hoặc không đủ. **Đồ án chưa xử lý** partial leak hay noise; bypass trong demo là ideal case (chương trình in trực tiếp địa chỉ).

---

## 2. Assumption học thuật (entropy)

- **Entropy = observed distribution:** Ước lượng H từ mẫu N lần; không biết phân phối thật của kernel.  
- **Sample size:** N = 500 chưa được justify bằng power analysis; mang tính thực nghiệm.  
- **Independence:** Các lần chạy coi là độc lập; thực tế có thể có tương quan (vd. fork không re-random trong một số trường hợp).  

→ **Good student / evaluation study, not research-grade inference.**

---

## 3. Tóm tắt

| Loại | Mô tả | Đồ án |
|------|--------|--------|
| Offset/address | Cố định cho 1 binary, 1 môi trường | Demo assumption; ghi trong config và REPRODUCIBILITY. |
| Success model | Cần probability, không chỉ 1 run | **Đã bổ sung:** exploit_success_probability.py (500 runs OFF vs ON). |
| Environment | Entropy/mmap cố định | Ghi môi trường; không biến hóa formal. |
| Leak | Luôn đúng, không noise | Ideal case; chưa xử lý partial/noise. |
| Entropy | Sample size, independence | Nêu trong Limitations; formal formula + Shannon + CI. |

*Tài liệu này dùng khi viết phần "Giới hạn" hoặc "Giả định" trong báo cáo; giúp giảng viên thấy đồ án ý thức rõ hardcoded/assumption.*
