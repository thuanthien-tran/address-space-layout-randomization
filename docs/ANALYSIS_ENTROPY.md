# Entropy analysis — Mô hình ước lượng và giải thích thống kê

Tài liệu mô tả **mô hình ước lượng entropy** và **cách diễn giải thống kê** cho phần đo entropy ASLR (GĐ4), bao gồm công thức, ý nghĩa và khoảng tin cậy.

---

## 1. Mô hình entropy (ước lượng)

### 1.1 Entropy của phân phối địa chỉ

Giả sử trong N lần chạy ta quan sát địa chỉ stack (buffer) và thu được **K giá trị khác nhau** (unique addresses). Một ước lượng đơn giản cho **entropy** (số bit thông tin / độ bất định) là:

- **Công thức (discrete empirical):**
  \[
  \hat{H} = \log_2(K)
  \]
  với K = số địa chỉ khác nhau trong mẫu.

- **Ý nghĩa:** Nếu không gian địa chỉ có khoảng \(2^{\hat{H}}\) “trạng thái” khả dĩ (trong mẫu), thì attacker đoán ngẫu nhiên một lần có xác suất thành công khoảng \(1/K \approx 1/2^{\hat{H}}\).

### 1.2 Ước lượng từ span (khoảng địa chỉ)

Gọi **span** = max(address) − min(address). Nếu địa chỉ được random theo alignment (vd. 16 byte), số “ô” khả dĩ có thể ước lượng là:

\[
\text{số ô} \approx \frac{\text{span}}{\text{alignment}} \quad \Rightarrow \quad \hat{H}_{\text{span}} = \log_2(\text{span}) - \log_2(\text{alignment})
\]

Trong script dùng **alignment = 1** (byte) để có cận trên: \(\hat{H}_{\text{span}} = \log_2(\text{span})\). Giá trị thực tế thường thấp hơn do kernel thường align (vd. 16 hoặc page).

### 1.3 So sánh hai ước lượng

| Ước lượng | Công thức | Ưu / nhược |
|-----------|-----------|------------|
| \(\hat{H}_{\text{unique}}\) | \(\log_2(K)\) | Phản ánh số trạng thái **thực sự xuất hiện** trong N lần; phụ thuộc N. |
| \(\hat{H}_{\text{span}}\) | \(\log_2(\text{span})\) | Phản ánh **khoảng** địa chỉ; không phụ thuộc N nhưng có thể overestimate nếu có “lỗ hổng” trong khoảng. |

Trong báo cáo có thể báo cáo cả hai và nêu: \(\hat{H}_{\text{unique}}\) thường dùng cho diễn giải “số trạng thái quan sát được”; \(\hat{H}_{\text{span}}\) cho “độ rộng không gian”.

---

## 2. Giải thích thống kê (statistical interpretation)

### 2.1 Phân phối địa chỉ

- Mẫu gồm N địa chỉ (có thể trùng). **Histogram** (số lần xuất hiện theo từng địa chỉ hoặc theo bin) mô tả **phân phối empirical** của địa chỉ stack khi ASLR bật.
- **Nhận xét:** Nếu ASLR hoạt động tốt, ta kỳ vọng phân phối **phân tán** (nhiều địa chỉ khác nhau, không tập trung ở một vài giá trị). Span lớn và K lớn tương ứng với entropy cao.

### 2.2 Xác suất đoán trúng (attacker)

- Nếu attacker đoán **ngẫu nhiên một địa chỉ** trong không gian đã quan sát (vd. K trạng thái), xác suất đoán trúng **một lần** xấp xỉ \(1/K \approx 2^{-\hat{H}_{\text{unique}}}\).
- **Ví dụ:** \(\hat{H}_{\text{unique}} \approx 20\) bit → xác suất \(\approx 1/2^{20} \approx 10^{-6}\). Điều này tương ứng với kết quả GĐ2: dùng địa chỉ cố định khi ASLR bật gần như luôn fail.

---

## 3. Khoảng tin cậy (confidence interval)

### 3.1 Ý tưởng

- **Entropy** \(\hat{H} = \log_2(K)\) phụ thuộc K (số địa chỉ khác nhau). K là biến ngẫu nhiên (phụ thuộc N lần chạy). Để phát biểu “entropy nằm trong khoảng [a, b] với độ tin cậy 95%”, ta cần **khoảng tin cậy (CI)** cho \(\hat{H}\) (hoặc cho K).
- **Cách đơn giản:** Dùng **bootstrap**: resample N lần từ danh sách địa chỉ (có hoàn lại), mỗi lần tính K và \(\hat{H}\); lấy phân vị 2.5% và 97.5% của \(\hat{H}\) qua các lần bootstrap → 95% CI cho entropy.

### 3.2 Công thức CI (gần đúng) cho K

Nếu coi mỗi lần chạy là “thử nghiệm” độc lập và địa chỉ có phân phối rời rạc với nhiều trạng thái, K (số giá trị khác nhau) có kỳ vọng và phương sai phức tạp. Trong thực hành, **bootstrap** là cách an toàn và script có thể báo cáo:

- **95% CI (bootstrap) cho entropy:** \([H_{2.5\%}, H_{97.5\%}]\) với H = log2(K) mỗi lần resample.

(Phần này được triển khai trong `entropy_measurement.py` khi bật tùy chọn CI.)

### 3.3 Ý nghĩa trong báo cáo

*"Entropy ước lượng là \(\hat{H}\) bit; 95% CI [a, b] phản ánh độ không chắc chắn do mẫu hữu hạn (N lần chạy). Khoảng càng hẹp khi N càng lớn."*

---

## 3b. Formal entropy estimation — Shannon entropy

**Công thức Shannon** cho phân phối rời rạc (discrete distribution):

\[
H = -\sum_{i} p_i \log_2(p_i)
\]

với \(p_i\) = xác suất (hoặc tần suất empirical) của trạng thái \(i\). Trong đồ án: mỗi “trạng thái” là một địa chỉ stack quan sát được; \(p_i = \text{count}_i / N\) với \(\text{count}_i\) = số lần địa chỉ \(i\) xuất hiện trong N lần chạy.

- **Ước lượng:** \(\hat{H}_{\text{shannon}} = -\sum_i \hat{p}_i \log_2(\hat{p}_i)\) với \(\hat{p}_i = \text{count}_i/N\).
- **So với H_unique:** \(\hat{H}_{\text{unique}} = \log_2(K)\) tương ứng với entropy **cực đại** khi có K trạng thái (phân phối đều). Khi phân phối **không đều**, \(\hat{H}_{\text{shannon}} \leq \log_2(K)\). Script báo cáo cả hai; H_shannon là ước lượng formal hơn từ empirical distribution.
- **Interpretation:** Entropy (bit) đo độ bất định; càng cao thì attacker càng khó đoán địa chỉ (xác suất đoán trúng thấp).

---

## 4. Limitations (giới hạn ước lượng)

| Giới hạn | Mô tả |
|----------|--------|
| **Sample size** | N = 500 chưa được justify bằng power analysis; kết quả mang tính thực nghiệm. |
| **Independence** | Các lần chạy coi là độc lập; có thể vi phạm (vd. fork không re-random trên một số hệ thống). |
| **Architecture** | Entropy phụ thuộc kiến trúc (x86-64) và kernel; không generalizable sang 32-bit / ARM. |
| **Observed vs true** | H ước lượng từ **mẫu**; phân phối thật của kernel không biết. |

→ *Good academic / evaluation study; không phải research-grade inference về phân phối thật.*

---

## 5. Tóm tắt cho báo cáo

- **Mô hình:** \(\hat{H}_{\text{unique}} = \log_2(K)\), \(\hat{H}_{\text{span}} = \log_2(\text{span})\), \(\hat{H}_{\text{shannon}} = -\sum p_i\log_2(p_i)\) (formal).
- **Giải thích:** Entropy cao → xác suất đoán trúng thấp → ASLR hiệu quả; gắn với kết quả GĐ2 (exploit fail).
- **Khoảng tin cậy:** 95% CI (bootstrap) cho entropy; **Limitations:** sample size, independence, architecture.

*Tài liệu này bổ sung cho EVALUATION_METRICS.md và script analysis/entropy_measurement.py.*
