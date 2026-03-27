# Evaluation Metrics — Chỉ số đánh giá hiệu quả ASLR

Tài liệu định nghĩa **các chỉ số đánh giá** (evaluation metrics) dùng trong đồ án để đánh giá hiệu quả mitigation ASLR một cách có hệ thống.

---

## 1. Mục đích

- Làm rõ **cái gì được đo** và **cách đánh giá** (không chỉ "chạy rồi mô tả").
- Cung cấp **formal evaluation** cho báo cáo: success rate, entropy, so sánh PIE.

---

## 2. Các chỉ số chính

### 2.1 Success rate của exploit (GĐ1, GĐ2)

| Chỉ số | Định nghĩa | Cách đo | Kỳ vọng |
|--------|-------------|---------|---------|
| **Success rate (ASLR OFF)** | Tỉ lệ lần chạy exploit mà shell được mở (vd. output có `uid=...`). | Chạy exploit N lần (vd. N=10), đếm success. | **100%** khi ASLR=0 (địa chỉ cố định). |
| **Success rate (ASLR ON, fixed addr)** | Tỉ lệ lần chạy exploit với **địa chỉ cố định** khi ASLR đang bật. | Script GĐ2: `--runs 50`, đếm success. | **0%** (hoặc rất thấp, do xác suất trùng địa chỉ ~ 1/2^entropy). |

**Ý nghĩa:** Success rate khi ASLR ON (fixed addr) **thấp** → ASLR **có hiệu quả** làm exploit không ổn định.

### 2.2 Success rate bypass (GĐ3)

| Chỉ số | Định nghĩa | Cách đo | Kỳ vọng |
|--------|-------------|---------|---------|
| **Bypass success (ASLR ON + leak)** | Tỉ lệ lần chạy exploit **có dùng leak** khi ASLR bật. | Chạy exploit_phase3_bypass_leak N lần. | **100%** (mỗi lần chạy có leak mới → địa chỉ đúng). |

**Ý nghĩa:** Khi có information leak, ASLR **không ngăn** được exploit → thể hiện **hạn chế** của ASLR.

### 2.3 Entropy (GĐ4)

| Chỉ số | Định nghĩa | Cách đo | Đơn vị / Ý nghĩa |
|--------|-------------|---------|-------------------|
| **Số địa chỉ khác nhau** | Số giá trị địa chỉ stack (buffer) khác nhau trong N lần chạy. | `entropy_measurement.py --runs N`, đếm `len(set(addresses))`. | Càng lớn → không gian càng phân tán. |
| **Span (khoảng địa chỉ)** | max(address) − min(address). | Từ cùng script. | Phản ánh vùng random (byte). |
| **Entropy ước lượng (bit)** | log2(số trạng thái khả dĩ). Có thể dùng log2(unique) hoặc log2(span/alignment). | Script in ra "Ước lượng entropy ~ x bit". | **Bit:** xác suất đoán trúng ~ 1/2^x. |

**Ý nghĩa:** Entropy càng cao → attacker càng khó đoán địa chỉ → mitigation mạnh hơn (với cùng điều kiện).

### 2.4 So sánh PIE vs non-PIE (GĐ5)

| Chỉ số | Định nghĩa | Cách đo | Kỳ vọng |
|--------|-------------|---------|---------|
| **Số giá trị địa chỉ main khác nhau (non-PIE)** | Khi ASLR=2, chạy binary **không PIE** N lần, đếm số giá trị địa chỉ main. | `compare_pie.py --runs 5`. | **1** (main cố định). |
| **Số giá trị địa chỉ main khác nhau (PIE)** | Khi ASLR=2, chạy binary **có PIE** N lần, đếm số giá trị địa chỉ main. | Cùng script. | **N** (hoặc gần N — main thay đổi mỗi lần). |

**Ý nghĩa:** PIE làm **thêm** vùng code random → tăng độ khó khai thác (gadget không cố định).

---

## 3. Tóm tắt cho báo cáo

| Giai đoạn | Metric chính | Kết luận ngắn |
|-----------|---------------|----------------|
| GĐ1 | Success rate (ASLR OFF) | 100% → lỗ hổng khai thác được. |
| GĐ2 | Success rate (ASLR ON, fixed addr) | 0% (hoặc rất thấp) → ASLR hiệu quả. |
| GĐ3 | Bypass success (leak) | 100% → info leak làm giảm hiệu quả ASLR. |
| GĐ4 | Entropy (bit), số địa chỉ khác nhau, span | Định lượng không gian random; xác suất đoán ~ 1/2^entropy. |
| GĐ5 | Địa chỉ main: 1 giá trị (non-PIE) vs N giá trị (PIE) | PIE tăng phạm vi random (gồm code). |

---

## 4. Giới hạn của metrics trong đồ án

- **Không** so sánh với các mitigation khác (canary, NX) bằng số liệu định lượng trong cùng đồ án.
- Entropy ước lượng **phụ thuộc** kernel, kiến trúc, số lần chạy; giá trị cụ thể mang tính minh họa.
- Success rate đo trên **một** binary và **một** kịch bản (buffer overflow + shellcode); không phải survey toàn bộ phần mềm.

*Tài liệu này dùng cho phần "Đánh giá định lượng" hoặc "Chỉ số đánh giá" trong báo cáo.*
