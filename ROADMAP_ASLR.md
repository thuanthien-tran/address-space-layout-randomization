# ROADMAP ĐỒ ÁN: ADDRESS SPACE LAYOUT RANDOMIZATION (ASLR)

**Môn học:** An toàn Hệ điều hành  
**Chuyên ngành:** Công nghệ thông tin – An ninh mạng  
**Mục tiêu:** Báo cáo đồ án kết thúc môn với demo ASLR từ A → Z, có kết quả rõ ràng và thuyết phục.

---

## PHẦN 0. MỤC TIÊU DEMO (NÓI VỚI THẦY)

> *"Đồ án phân tích hiệu quả ASLR trong việc ngăn chặn khai thác Buffer Overflow thông qua thực nghiệm: exploit khi ASLR tắt, chứng minh fail khi ASLR bật, bypass bằng leak, đo entropy và so sánh PIE."*

**Lưu ý:** Luôn mở đầu báo cáo/demo bằng câu này để thầy nắm rõ mục đích.

---

## PHẦN 1. LỘ TRÌNH PHÁT TRIỂN PROJECT (5 GIAI ĐOẠN THỰC NGHIỆM)

| Giai đoạn | Nội dung | Đầu ra |
|-----------|----------|--------|
| **GĐ1** | Exploit thành công khi ASLR OFF | Payload overwrite RET, shellcode, shell ổn định (`exploit_phase1_aslr_off.py`) |
| **GĐ2** | Exploit FAIL khi ASLR ON | Chạy nhiều lần với địa chỉ cố định → crash / 0% success (`exploit_phase2_aslr_on_fail.py`) |
| **GĐ3** | Bypass ASLR (lite) | Leak địa chỉ buffer → dùng làm RET → shell khi ASLR bật (`exploit_phase3_bypass_leak.py`) |
| **GĐ4** | Đo entropy ASLR (định lượng) | Chạy 500 lần, thu stack address, CSV + thống kê + histogram (`analysis/entropy_measurement.py`) |
| **GĐ5** | So sánh PIE vs non-PIE | Bảng địa chỉ main/buffer, nhận xét độ khó khai thác (`analysis/compare_pie.py`) |

Chi tiết lệnh chạy từng giai đoạn: **exploits/README_EXPLOITS.md**.

---

## PHẦN 1b. LỘ TRÌNH TỔNG QUAN (BÁO CÁO & THỜI GIAN)

| Giai đoạn | Nội dung | Thời gian gợi ý | Đầu ra |
|-----------|----------|-----------------|--------|
| **1** | Nghiên cứu lý thuyết ASLR | 1–2 tuần | Slide/bản tóm tắt: ASLR là gì, mức độ trên Linux, ưu/nhược |
| **2** | Chuẩn bị môi trường + code demo + exploit | 3–5 ngày | Ubuntu, `aslr_demo.c`, script GĐ1–GĐ5 |
| **3** | Thực hành demo (ASLR OFF/ON) + exploit + entropy | 2–3 ngày | Kết quả chạy, bảng địa chỉ, entropy, PIE |
| **4** | Phần "tác động đến khai thác" + bypass | 1–2 ngày | Giải thích tại sao exploit khó khi ASLR bật; info leak bypass |
| **5** | Viết báo cáo + slide báo cáo | 1–2 tuần | Báo cáo Word/PDF, slide thuyết trình |
| **6** | Tập demo và dự phòng lỗi | 2–3 ngày | Script demo, checklist, xử lý lỗi thường gặp |

---

## PHẦN 2. CHUẨN BỊ MÔI TRƯỜNG

### 2.1 Hệ điều hành

- **Ubuntu Linux** (bản cài trực tiếp hoặc VM đều được).
- Mở **Terminal** để thực hiện toàn bộ lệnh.

### 2.2 Kiểm tra ASLR hiện tại

```bash
cat /proc/sys/kernel/randomize_va_space
```

- **0** → ASLR tắt  
- **1** → Randomize stack, libraries, mmap (một phần)  
- **2** → ASLR đầy đủ (stack, heap, libraries, mmap) — **thường dùng**

**Câu nói với thầy:**  
*"Linux hỗ trợ nhiều mức ASLR; demo này dùng mức 0 và 2 để so sánh."*

---

## PHẦN 3. VIẾT VÀ BIÊN DỊCH CHƯƠNG TRÌNH DEMO

### 3.1 Tạo file `aslr_demo.c`

- Nằm trong thư mục **demo_aslr/** của project.
- Nội dung: có buffer overflow (`gets`), in địa chỉ **main** (executable), **printf** (thư viện), **buffer** (stack), **heap** (malloc) để quan sát ASLR toàn bộ không gian địa chỉ.

### 3.2 Compile (tắt các cơ chế bảo vệ khác)

```bash
cd demo_aslr
gcc aslr_demo.c -fno-stack-protector -z execstack -no-pie -o aslr_demo
```

**Giải thích khi demo:**

| Flag | Ý nghĩa |
|------|--------|
| `-fno-stack-protector` | Tắt stack canary |
| `-no-pie` | Tắt PIE → địa chỉ executable cố định, dễ quan sát |
| `-z execstack` | Stack được phép thực thi (phục vụ demo exploit) |

**Mục đích:** Chỉ tập trung vào ảnh hưởng của ASLR, không bị nhiễu bởi canary hay PIE.

---

## PHẦN 4. DEMO PHẦN 1 – ASLR TẮT

### 4.1 Tắt ASLR

```bash
sudo sysctl -w kernel.randomize_va_space=0
```

### 4.2 Chạy chương trình nhiều lần

```bash
./aslr_demo
./aslr_demo
./aslr_demo
```

**Quan sát:** Địa chỉ main, printf, buffer, heap.

**Kết quả mong đợi:** Địa chỉ **giống nhau** mỗi lần chạy.

**Câu nói:**  
*"Khi ASLR bị tắt, layout bộ nhớ tiến trình là cố định."*

---

## PHẦN 5. DEMO PHẦN 2 – ASLR BẬT

### 5.1 Bật ASLR

```bash
sudo sysctl -w kernel.randomize_va_space=2
```

### 5.2 Chạy lại chương trình

```bash
./aslr_demo
./aslr_demo
./aslr_demo
```

**Quan sát:** Địa chỉ main, printf, buffer, heap **thay đổi** mỗi lần.

**Kết quả mong đợi:** Mỗi lần chạy là một layout khác nhau.

**Câu nói:**  
*"ASLR làm cho kẻ tấn công không thể đoán chính xác vị trí bộ nhớ của payload."*

---

## PHẦN 6. DEMO PHẦN 3 – TÁC ĐỘNG ĐẾN KHAI THÁC (VÀ BYPASS)

- **Khi ASLR OFF:** Biết trước địa chỉ buffer → overwrite return address → khai thác ổn định (GĐ1).
- **Khi ASLR ON:** Payload dùng địa chỉ cố định sẽ fail; chạy nhiều lần → crash / 0% success (GĐ2).
- **Bypass (GĐ3):** Nếu chương trình leak địa chỉ (vd. in ra buffer), attacker dùng địa chỉ đó làm RET → vẫn có thể lấy shell khi ASLR bật. → *"ASLR không vá lỗ hổng; info leak làm giảm hiệu quả."*

**Câu nói:**  
*"ASLR không vá lỗ hổng, nhưng làm exploit trở nên không ổn định. Khi có information leak, attacker có thể bypass ASLR (demo GĐ3)."*

---

## PHẦN 7. TỔNG KẾT DEMO (NÓI RÕ – NGẮN – CHUẨN)

Kết luận nên có:

1. ASLR **random hóa** không gian địa chỉ tiến trình.
2. **ASLR tắt:** địa chỉ cố định → dễ khai thác.
3. **ASLR bật:** địa chỉ thay đổi → exploit khó thành công.
4. ASLR là **một lớp phòng thủ** quan trọng nhưng **không tuyệt đối** (có thể kết hợp info leak, brute-force trong một số trường hợp).

---

## PHẦN 8. CÁC LỖI THƯỜNG GẶP (TRÁNH KHI DEMO)

| Lỗi | Hậu quả | Cách tránh |
|-----|---------|------------|
| Compile quên `-no-pie` | Địa chỉ `main` vẫn thay đổi dù ASLR tắt | Luôn dùng đủ flags khi compile |
| Quên bật/tắt ASLR | Demo không thấy khác biệt | Sau mỗi lần đổi mức, chạy `cat /proc/sys/kernel/randomize_va_space` |
| Ubuntu/GCC mới, quên tắt bảo vệ | Canary/PIE vẫn bật, demo không rõ | Dùng đúng lệnh `gcc` với `-fno-stack-protector -no-pie -z execstack` |

---

## PHẦN 9. CẤU TRÚC BÁO CÁO ĐỒ ÁN GỢI Ý

1. **Mở đầu:** Đặt vấn đề, mục tiêu đồ án, câu "Mục tiêu demo" như trên.
2. **Formal models:** Nêu **Formal Threat Model** (scope, A1–A5, S1–S3) và **Formal Entropy Model** (H = log2(K), P_guess, 95% CI) — tóm tắt: **FORMAL_MODELS.md**; chi tiết: **THREAT_MODEL.md**, **docs/ANALYSIS_ENTROPY.md**.
3. **Cơ sở lý thuyết:** ASLR là gì, các mức trên Linux, liên hệ stack/heap/executable. Bổ sung **entropy**, **hạn chế ASLR**, **userland vs KASLR** (xem **LY_THUYET_VA_MO_RONG.md**).
4. **Môi trường và công cụ:** Ubuntu, GCC, cách kiểm tra `randomize_va_space`. **Reproducibility:** xem **REPRODUCIBILITY.md** (phiên bản, bước chạy, offsets).
5. **Thiết kế chương trình demo:** Giải thích `aslr_demo.c` (in địa chỉ main, printf, buffer, heap), lý do dùng `gets`, các flag compile. Có thể thêm so sánh **PIE vs không PIE** (bảng trong LY_THUYET_VA_MO_RONG.md).
6. **Kết quả thực nghiệm:**  
   - Bảng/screenshot địa chỉ khi ASLR=0 và ASLR=2 (có thể dùng bảng mẫu và **demo_log.txt** từ script `./demo_commands.sh --log`).  
   - **GĐ1–GĐ3:** Kết quả exploit khi ASLR OFF (thành công), khi ASLR ON với fixed addr (thất bại), và bypass bằng leak.  
   - **GĐ4:** Bảng/phân phối entropy (stack address qua N lần chạy), file **analysis/entropy_histogram.png** và **stack_addresses.csv**.  
   - **GĐ5:** Bảng so sánh PIE vs non-PIE (địa chỉ main, buffer khi ASLR=2).  
   - Nhận xét: cố định vs thay đổi; ASLR áp dụng cho stack, heap, thư viện (và executable nếu PIE).
7. **Đánh giá định lượng:** Dùng **EVALUATION_METRICS.md** — success rate (GĐ1, GĐ2, GĐ3), entropy (GĐ4), so sánh PIE (GĐ5).
8. **Tác động đến khai thác:** Giải thích ngắn gọn; demo GĐ2 (fail) và GĐ3 (bypass); nêu **hạn chế** (info leak, ROP bypass) như trong LY_THUYET_VA_MO_RONG.md. Có thể nêu **modern mitigations** (DEFENSE.md).
9. **Kết luận và hướng phát triển:** Tóm tắt, giới hạn của ASLR, liên hệ Windows/Android/CVE (mô tả ngắn), kết hợp DEP, stack canary, PIE.

---

## PHẦN 10. CHECKLIST TRƯỚC KHI BÁO CÁO

- [ ] Đã chạy demo ASLR OFF/ON và ghi lại kết quả (screenshot hoặc bảng).
- [ ] **GĐ1:** Đã chạy exploit khi ASLR OFF và thấy shell (uid=...).
- [ ] **GĐ2:** Đã chạy exploit với fixed addr khi ASLR ON, ghi lại tỉ lệ success (0% hoặc rất thấp).
- [ ] **GĐ3:** Đã chạy bypass bằng leak khi ASLR ON và thấy shell.
- [ ] **GĐ4:** Đã chạy entropy_measurement.py (vd. 500 lần), lưu CSV và histogram cho báo cáo.
- [ ] **GĐ5:** Đã chạy compare_pie.py và điền bảng so sánh PIE vs non-PIE.
- [ ] Đã kiểm tra `randomize_va_space` trước mỗi phần demo.
- [ ] Đã compile với đủ flags: `-fno-stack-protector -z execstack -no-pie` (và `make pie` cho GĐ5).
- [ ] Đã chuẩn bị câu nói cho từng phần (Phần 4, 5, 6, 7).
- [ ] Đã đọc phần "Lỗi thường gặp" và tập xử lý (ví dụ quên tắt ASLR thì làm lại).
- [ ] Báo cáo và slide đã có đủ: mục tiêu, threat model, lý thuyết, môi trường, reproducibility, kết quả 5 giai đoạn, evaluation metrics, entropy, PIE, kết luận.
- [ ] Đã tham khảo **THREAT_MODEL.md**, **REPRODUCIBILITY.md**, **EVALUATION_METRICS.md**, **LY_THUYET_VA_MO_RONG.md**, **DEFENSE.md**.
- [ ] (Tùy chọn) Đã chạy `./demo_commands.sh --log` và lưu `demo_log.txt` để minh họa báo cáo.

---

*Roadmap này được soạn để đồ án ASLR thực hiện đúng trọng tâm, demo rõ ràng và báo cáo đạt yêu cầu môn An toàn Hệ điều hành. Lý thuyết mở rộng (entropy, hạn chế, PIE, sơ đồ, bảng): xem **LY_THUYET_VA_MO_RONG.md**.*
