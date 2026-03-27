# Formal Models — Threat Model & Entropy Model

Đồ án cung cấp **hai mô hình chính thức** (formal models) để đánh giá hiệu quả ASLR: **Formal Threat Model** và **Formal Entropy Model**. Tài liệu này tóm tắt định nghĩa và công thức; chi tiết đầy đủ nằm trong **THREAT_MODEL.md** và **docs/ANALYSIS_ENTROPY.md**.

---

## 1. Formal Threat Model

**Vị trí đầy đủ:** [THREAT_MODEL.md](THREAT_MODEL.md)

### 1.1 Định nghĩa

- **Scope:** ASLR **userland** (stack, heap, mmap, DSO); không bao gồm KASLR.
- **Lỗ hổng:** Buffer overflow (ghi đè return address).
- **Mục tiêu attacker:** Code execution (shellcode / ROP).

### 1.2 Assets & Assumptions

| Ký hiệu | Định nghĩa |
|--------|------------|
| **Asset** | Quyền thực thi mã tùy ý trong tiến trình. |
| **A1** | Attacker có thể cung cấp input dài tùy ý (stdin). |
| **A2** | Attacker biết offset từ buffer tới return address. |
| **A3** | Không canary/NX trong demo (cô lập ASLR). |
| **A4** | Môi trường Linux x86-64. |
| **A5** | (GĐ3) Attacker có information leak (địa chỉ buffer). |

### 1.3 Attack Scenarios (formal)

| Scenario | Điều kiện | Hành động | Kết quả đo |
|----------|-----------|-----------|-------------|
| **S1** | ASLR OFF | Payload với địa chỉ buffer cố định | Success rate ≈ 100% |
| **S2** | ASLR ON, không leak | Payload với địa chỉ cố định (từ S1) | Success rate ≈ 0% |
| **S3** | ASLR ON, có leak | Payload với địa chỉ lấy từ leak | Success rate ≈ 100% |

→ **Formal threat model** cho phép phát biểu giả thuyết H1–H3 và đánh giá mitigation một cách có hệ thống (xem **docs/EXPERIMENT_DESIGN.md**).

---

## 2. Formal Entropy Model

**Vị trí đầy đủ:** [docs/ANALYSIS_ENTROPY.md](docs/ANALYSIS_ENTROPY.md)

### 2.1 Định nghĩa và ký hiệu

- **N:** Số lần chạy chương trình (mẫu).
- **K:** Số địa chỉ stack (buffer) **khác nhau** trong N lần (unique count).
- **Span:** \( S = \max(\text{address}) - \min(\text{address}) \).

### 2.2 Công thức entropy (formal)

**Ước lượng từ số trạng thái:** \(\hat{H}_{\text{unique}} = \log_2(K)\) [bit].

**Shannon entropy (formal):** \(H = -\sum_i p_i \log_2(p_i)\) với \(p_i\) = tần suất địa chỉ \(i\) trong mẫu. Script báo cáo \(\hat{H}_{\text{shannon}}\).

**Ước lượng từ độ rộng (cận trên):** \(\hat{H}_{\text{span}} = \log_2(S)\) [bit].

### 2.3 Ý nghĩa hình thức

- **Xác suất đoán trúng (một lần):** \( P_{\text{guess}} \approx 1/K = 2^{-\hat{H}_{\text{unique}}} \).
- **Statistical interpretation:** Entropy càng cao → attacker càng khó đoán địa chỉ → mitigation càng hiệu quả (tương ứng GĐ2: success rate ≈ 0%).

### 2.4 Khoảng tin cậy (95% CI)

- **Phương pháp:** Bootstrap: resample N lần từ mẫu địa chỉ (có hoàn lại), mỗi lần tính \( K_b \), \( \hat{H}_b = \log_2(K_b) \); lấy phân vị 2.5% và 97.5% của \( \hat{H}_b \).
- **Kết quả:** 95% CI cho entropy: \( [H_{2.5\%},\, H_{97.5\%}] \) (triển khai trong `analysis/entropy_measurement.py --ci 500`).

---

## 3. Trích dẫn cho báo cáo

- **Formal threat model:** *"Đồ án sử dụng formal threat model (THREAT_MODEL.md) với scope userland ASLR, assets và assumptions A1–A5, và ba attack scenarios S1–S3 để đánh giá hiệu quả mitigation."*
- **Formal entropy model:** *"Entropy được ước lượng theo formal model (docs/ANALYSIS_ENTROPY.md): \(\hat{H} = \log_2(K)\) với K là số địa chỉ khác nhau; xác suất đoán trúng \(2^{-\hat{H}}\); 95% CI bằng bootstrap."*

---

| Mô hình | File đầy đủ | Tóm tắt |
|---------|-------------|---------|
| **Formal Threat Model** | THREAT_MODEL.md | Scope, assets, A1–A5, S1–S3 |
| **Formal Entropy Model** | docs/ANALYSIS_ENTROPY.md | \( \hat{H} = \log_2(K) \), Shannon \(-\sum p_i\log_2 p_i\), P_guess, 95% CI, Limitations |
