# Đồ án: Phân tích hiệu quả ASLR trong việc ngăn chặn khai thác Buffer Overflow

**Môn học:** An toàn Hệ điều hành  
**Chuyên ngành:** Công nghệ thông tin – An ninh mạng

## Hướng đồ án

Phân tích hiệu quả ASLR trong việc ngăn chặn khai thác Buffer Overflow **thông qua thực nghiệm exploit**: có code, có attack, có defense, có analysis và research nhẹ — phù hợp đồ án OS Security và CV Security.

## Mục tiêu

- Chứng minh **buffer overflow** có thể khai thác khi **ASLR tắt** (exploit ổn định).
- Chứng minh **ASLR bật** làm exploit với địa chỉ cố định **thất bại** (crash/random).
- Thể hiện **bypass ASLR** (lite): leak địa chỉ → tính offset → exploit lại khi ASLR bật.
- **Đo entropy ASLR** (định lượng): chạy nhiều lần, thu địa chỉ stack, phân phối và thống kê.
- **So sánh PIE vs non-PIE** về khả năng random hóa và độ khó khai thác.

## Cấu trúc project

```
Address Space Layout Randomization/
├── README.md                    ← Bạn đang đọc
├── run_all_kali.sh              ← Chạy tuần tự toàn bộ demo trên Kali/Ubuntu VM
├── ROADMAP_ASLR.md              ← Lộ trình chi tiết (lý thuyết + demo + báo cáo)
├── LY_THUYET_VA_MO_RONG.md      ← Lý thuyết: entropy, hạn chế ASLR, PIE, userland vs KASLR, sơ đồ
├── TAI_LIEU_THAM_KHAO.md        ← Tài liệu trích dẫn cho báo cáo
├── FORMAL_MODELS.md             ← Tóm tắt Formal Threat Model + Formal Entropy Model (trích dẫn báo cáo)
├── THREAT_MODEL.md              ← Mô hình mối đe dọa (phạm vi, kịch bản, giả định)
├── REPRODUCIBILITY.md           ← Tái lập thực nghiệm (môi trường, bước chạy, offsets)
├── EVALUATION_METRICS.md        ← Chỉ số đánh giá (success rate, entropy, PIE)
├── DEFENSE.md                   ← ASLR + defense in depth + modern mitigations
├── docs/                        ← Độ sâu hệ thống và thiết kế
│   ├── SYSTEM_LEVEL_DEPTH.md    ← KASLR, entropy theo kiến trúc, loader mapping
│   ├── EXPLOIT_DESIGN.md        ← Demonstration vs production, offset config, reliability
│   ├── ANALYSIS_ENTROPY.md      ← Mô hình entropy, giải thích thống kê, CI
│   └── EXPERIMENT_DESIGN.md     ← Thiết kế thí nghiệm: giả thuyết, biến số, cỡ mẫu
├── demo_aslr/                   ← Chương trình vulnerable + build
│   ├── aslr_demo.c              ← Chương trình in địa chỉ (main, printf, buffer, heap) + gets()
│   ├── Makefile                 ← aslr_demo, aslr_demo_pie, aslr_demo_nx (NX ON)
│   ├── get_fixed_addr.sh        ← Lấy địa chỉ buffer khi ASLR OFF (cho Giai đoạn 2)
│   ├── README_DEMO.md           ← Hướng dẫn chạy demo
│   └── demo_commands.sh         ← Script demo ASLR OFF/ON
├── exploits/                    ← Exploit và bypass
│   ├── README_EXPLOITS.md       ← Hướng dẫn từng giai đoạn
│   ├── exploit_config.py        ← Cấu hình chung: offset, shellcode, đường dẫn binary
│   ├── exploit_phase1_aslr_off.py   ← Giai đoạn 1: exploit khi ASLR OFF
│   ├── exploit_phase2_aslr_on_fail.py ← Giai đoạn 2: exploit fail khi ASLR ON (fixed addr)
│   ├── exploit_phase3_bypass_leak.py ← Giai đoạn 3: bypass ASLR bằng leak
│   └── exploit_phase4_rop.py    ← Giai đoạn 4: ROP bypass NX + ASLR (ret2libc)
└── analysis/                    ← Phân tích định lượng
    ├── entropy_measurement.py   ← Giai đoạn 4: entropy (H_unique, Shannon, CI, limitations)
    ├── exploit_success_probability.py ← Success probability: N runs OFF vs ON, plot
    ├── mitigation_matrix.py     ← Bảng so sánh mitigation (No protection → NX+ROP)
    └── compare_pie.py           ← Giai đoạn 5: so sánh PIE vs non-PIE
```

## Lộ trình 5 giai đoạn (chuẩn đồ án)

| Giai đoạn | Nội dung | Đầu ra |
|-----------|----------|--------|
| **1** | Exploit thành công khi ASLR OFF | Payload overwrite RET, shellcode, shell ổn định |
| **2** | Exploit FAIL khi ASLR ON | Chạy nhiều lần với địa chỉ cố định → crash/0% success |
| **3** | Bypass ASLR (lite) | Leak địa chỉ buffer → dùng làm RET → shell khi ASLR bật |
| **4** | Đo entropy ASLR | Chạy 500 lần, thu stack address, CSV + thống kê + histogram |
| **5** | So sánh PIE vs non-PIE | Bảng địa chỉ main/buffer, nhận xét độ khó khai thác |

## Bắt đầu nhanh (Linux)

1. **Chuẩn bị:** Ubuntu (hoặc VM/WSL), `gcc`, `python3`.
2. **Build:**
   ```bash
   cd demo_aslr
   make          # aslr_demo (no PIE)
   make pie      # aslr_demo_pie cho Giai đoạn 5
   make nx       # aslr_demo_nx cho ROP phase4
   ```
3. **Giai đoạn 1 — Exploit khi ASLR OFF:**
   ```bash
   sudo sysctl -w kernel.randomize_va_space=0
   python3 ../exploits/exploit_phase1_aslr_off.py
   ```
   → Kỳ vọng: in ra `uid=...` (shell đã mở).
4. **Giai đoạn 2 — Fail khi ASLR ON:** Xem `exploits/README_EXPLOITS.md` (lấy fixed addr rồi chạy với ASLR=2).
5. **Giai đoạn 3 — Bypass leak:** ASLR=2, chạy `exploit_phase3_bypass_leak.py`.
6. **Giai đoạn 4 — ROP bypass NX+ASLR:** `make nx` rồi `python3 ../exploits/exploit_phase4_rop.py`.
7. **Giai đoạn 5 — Entropy:** `python3 ../analysis/entropy_measurement.py --runs 500 --ci 500`.
8. **Giai đoạn 6 — PIE:** `make both` rồi `python3 ../analysis/compare_pie.py --runs 5`.

### Chạy một lệnh trên Kali VM

```bash
cd "Address Space Layout Randomization"
chmod +x run_all_kali.sh
./run_all_kali.sh
```

Script sẽ chạy tuần tự phase 1→4, mitigation matrix, probability model, entropy và PIE (có pause để bạn theo dõi/chụp màn hình).

## Yêu cầu môi trường

- **Hệ điều hành:** Ubuntu Linux (cài trực tiếp hoặc VM/WSL).
- **Công cụ:** `gcc` (build-essential), `python3`. Tùy chọn: `matplotlib` cho histogram (Giai đoạn 4).

## Liên hệ nội dung

| Nhu cầu | Tài liệu |
|--------|----------|
| Lộ trình từng bước, câu nói khi báo cáo, lỗi thường gặp | **ROADMAP_ASLR.md** |
| Entropy, hạn chế ASLR, PIE, userland vs KASLR, sơ đồ, bảng mẫu | **LY_THUYET_VA_MO_RONG.md** |
| **Formal Threat Model** + **Formal Entropy Model** (tóm tắt, trích dẫn) | **FORMAL_MODELS.md** |
| Mô hình đe dọa, phạm vi, kịch bản tấn công (chi tiết) | **THREAT_MODEL.md** |
| Tái lập kết quả: môi trường, bước chạy, offsets | **REPRODUCIBILITY.md** |
| Chỉ số đánh giá: success rate, entropy, PIE | **EVALUATION_METRICS.md** |
| Lệnh exploit từng giai đoạn | **exploits/README_EXPLOITS.md** |
| Defense in depth, modern mitigations (CFI, SafeStack, CET) | **DEFENSE.md** |
| Độ sâu hệ thống: KASLR, kiến trúc, loader | **docs/SYSTEM_LEVEL_DEPTH.md** |
| Thiết kế exploit, offset config, reliability | **docs/EXPLOIT_DESIGN.md** |
| Hardcoded / assumption nguy hiểm, limitations | **docs/ASSUMPTIONS_AND_LIMITATIONS.md** |
| Exploit success probability (500 runs OFF vs ON) | **analysis/exploit_success_probability.py** |
| Mô hình entropy, thống kê, CI | **docs/ANALYSIS_ENTROPY.md** |
| Thiết kế thí nghiệm (giả thuyết, biến số) | **docs/EXPERIMENT_DESIGN.md** |
| Trích dẫn, tài liệu tham khảo | **TAI_LIEU_THAM_KHAO.md** |
