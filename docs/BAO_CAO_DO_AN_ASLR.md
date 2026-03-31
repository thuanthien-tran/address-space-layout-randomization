# BÁO CÁO ĐỒ ÁN

## Đề tài
**Address Space Layout Randomization (ASLR)**: phân tích hiệu quả trong ngăn chặn khai thác Buffer Overflow.

## Chương 1. Tổng quan đề tài

### 1.1 Lý do chọn đề tài
- Buffer overflow là nhóm lỗi kinh điển, có tính thực tiễn cao trong ATTT.
- ASLR là cơ chế phòng thủ quan trọng trên các hệ điều hành hiện đại.
- Đồ án cho phép kết hợp lý thuyết, kỹ thuật khai thác và đánh giá định lượng.

### 1.2 Mục tiêu nghiên cứu
- Chứng minh khả năng khai thác khi ASLR tắt.
- Chứng minh khai thác bằng địa chỉ cố định thất bại khi ASLR bật.
- Trình bày kỹ thuật bypass ASLR thông qua information leak.
- Đánh giá định lượng bằng success rate, entropy ước lượng và so sánh PIE/non-PIE.

### 1.3 Đối tượng và phạm vi
- Đối tượng: chương trình C có lỗi stack buffer overflow.
- Phạm vi: user-space trên Linux x86-64, không đi sâu KASLR/kernel exploit.
- Các biện pháp/mitigations xem xét: ASLR, NX, PIE; minh họa ROP ret2libc.
> [NOTE chèn hình cụ thể] **Hình 1.1 - Phạm vi đề tài** 8:11 PM 3/30/20268:11 PM 3/30/2026 
> Nội dung cần thể hiện: In-scope (user-space, ASLR/NX/PIE, demo 5 phase), Out-of-scope (kernel exploit/KASLR).  
> Nguồn hình: tự vẽ (PowerPoint/draw.io).

### 1.4 Câu hỏi nghiên cứu
- ASLR làm giảm xác suất exploit theo cách nào?
- Information leak ảnh hưởng đến hiệu quả ASLR ra sao?
- PIE bổ sung gì cho ASLR trong bối cảnh khai thác?

### 1.5 Đóng góp chính của đồ án
- Xây dựng bộ demo 5 giai đoạn có thể tái lập.
- Xây dựng script tự động hóa “run-to-report”.
- Bộ tiêu chí đánh giá và tài liệu hóa threats/limitations.

## Chương 2. Cơ sở lý thuyết

### 2.1 Kiến thức nền tảng
#### 2.1.1 Vùng executable
#### 2.1.2 Vùng stack
#### 2.1.3 Vùng heap
#### 2.1.4 Thư viện dùng chung (shared libraries)
> [NOTE chèn hình cụ thể] **Hình 2.1 - Memory layout tiến trình**  
> Bắt buộc có: `text`, `libc`, `heap`, `stack`, và chiều tăng/giảm địa chỉ.  
> Nguồn hình: tự vẽ theo kiến trúc Linux x86-64.

### 2.2 Cơ chế tấn công
#### 2.2.1 Cơ chế ghi đè return address
#### 2.2.2 Vai trò của offset và stack frame
#### 2.2.3 Điều kiện để khai thác thành công
> [NOTE chèn hình cụ thể] **Hình 2.2 - Stack frame trước/sau overflow**  
> Bắt buộc có: `buffer[64]`, saved `RBP`, saved `RIP`, vị trí `OFFSET_RET`.  
> Nguồn số liệu: `exploits/exploit_config.py` và `demo_aslr/aslr_demo.c`.

### 2.3 Cơ chế phòng vệ
#### 2.3.1 Nguyên lý random hóa địa chỉ
#### 2.3.2 randomize_va_space (0/1/2)
#### 2.3.3 Entropy và ý nghĩa bảo mật
> [NOTE chèn hình cụ thể] **Hình 2.3 - So sánh ASLR OFF vs ON**  
> Dạng nên dùng: bảng hoặc 2 ảnh terminal đặt cạnh nhau (ASLR=0 địa chỉ lặp lại, ASLR=2 địa chỉ thay đổi).  
> Lệnh tạo dữ liệu: chạy `./aslr_demo` nhiều lần với `sudo sysctl -w kernel.randomize_va_space=0/2`.

### 2.4 Các thành phần liên quan
#### 2.4.1 NX (Non-Executable stack)
#### 2.4.2 PIE (Position Independent Executable)
#### 2.4.3 ROP/ret2libc và vai trò gadget
> [NOTE chèn hình cụ thể] **Hình 2.4 - NX và ý tưởng ROP**  
> Nên có 2 phần: (1) NX chặn thực thi stack, (2) ret2libc/ROP gọi `system("/bin/sh")`.

### 2.5 Nhận xét và giới hạn
#### 2.5.1 Information leak
#### 2.5.2 Brute-force trong bối cảnh thực tế
#### 2.5.3 Sự cần thiết của defense-in-depth

## Chương 3. Phân tích và thiết kế hệ thống demo

### 3.1 Tổng quan hệ thống
#### 3.1.1 Thành phần demo_aslr
#### 3.1.2 Thành phần exploits
#### 3.1.3 Thành phần analysis
#### 3.1.4 Thành phần docs/tools
> [NOTE chèn sơ đồ cụ thể] **Hình 3.1 - Kiến trúc tổng thể dự án**  
> Bắt buộc có luồng: `demo_aslr` -> `exploits` -> `analysis` -> `tools/report_pack.sh` -> `artifacts/`.

### 3.2 Thành phần thực thi
#### 3.2.1 aslr_demo.c và hàm vuln()
#### 3.2.2 Các thông số build (no-pie, execstack, nx)
#### 3.2.3 Luồng in leak địa chỉ (main/printf/buffer/heap)
> [NOTE chèn hình cụ thể] **Hình 3.2 - Luồng chạy aslr_demo**  
> Chụp terminal có đủ 4 dòng: `main`, `printf`, `buffer`, `heap`.  
> Nguồn: chạy `./demo_aslr/aslr_demo` (hoặc từ log phase).

### 3.3 Quy trình triển khai
#### 3.3.1 Giai đoạn 1: ASLR OFF (shellcode success)
#### 3.3.2 Giai đoạn 2: ASLR ON + fixed address (expected fail)
#### 3.3.3 Giai đoạn 3: ASLR ON + leak bypass
#### 3.3.4 Giai đoạn 4: NX + ASLR + ROP ret2libc
#### 3.3.5 Giai đoạn 5: So sánh PIE vs non-PIE
> [NOTE chèn sơ đồ cụ thể] **Hình 3.3 - Lưu đồ 5 giai đoạn**  
> Bắt buộc ghi rõ điều kiện từng phase:  
> P1 (ASLR OFF), P2 (ASLR ON + fixed), P3 (ASLR ON + leak), P4 (NX + ROP), P5 (PIE compare).

### 3.4 Cấu hình hệ thống
#### 3.4.1 OFFSET_RET và RET_DELTA
#### 3.4.2 Shellcode marker uid=1337
#### 3.4.3 Điều kiện môi trường để tái lập đề tài
> [NOTE chèn bảng cụ thể] **Bảng 3.1 - Tham số cấu hình chính**  
> Cột gợi ý: `Tham số`, `Giá trị`, `Ý nghĩa`, `File cấu hình`.  
> Hàng tối thiểu: `OFFSET_RET`, `RET_DELTA`, `SHELLCODE marker`, `binary path`, `build flags`.

### 3.5 Yêu cầu hệ thống
#### 3.5.1 Yêu cầu chức năng (Functional Requirements)
- FR1: Build được các binary trong `demo_aslr/` theo các cấu hình cần thiết (no-PIE/PIE/NX).
- FR2: Chạy được chuỗi demo chuẩn theo thứ tự phase (Phase 1 → Phase 5) thông qua `run_all_kali.sh` hoặc chế độ nhanh `run_all_kali_quick.sh`.
- FR3: Các exploit phase in ra thông tin leak (khi có) và tạo marker thành công để phục vụ đối chiếu kết quả.
- FR4: Tổng hợp được kết quả thực nghiệm theo từng phase và xuất ra các log/artifact phục vụ báo cáo (`analysis/` và `tools/report_pack.sh`).
- FR5: Thực hiện được các phép đo định lượng: success rate, entropy ước lượng, so sánh PIE vs non-PIE và lập mitigation matrix.

#### 3.5.2 Yêu cầu phi chức năng (Non-Functional Requirements)
- NFR1: Tính tái lập (reproducibility): chạy lại cho ra xu hướng kết quả ổn định trong cùng điều kiện thí nghiệm.
- NFR2: Tính ổn định pipeline: hạn chế treo/hang do I/O nhờ cơ chế unbuffered/stdout flush trong binary và wrapper khi chạy subprocess.
- NFR3: Tính vững khi lỗi: nếu không đạt điều kiện marker/leak ở một phase, hệ thống cần dừng hoặc cảnh báo để tránh tạo số liệu sai.
- NFR4: Tính phù hợp môi trường: hoạt động trên Kali/Ubuntu x86-64 với quyền điều khiển ASLR (sysctl) trong bối cảnh mô phỏng.
- NFR5: Hiệu quả thời gian: có chế độ quick để kiểm tra nhanh, đồng thời có chế độ full để thu đủ thống kê cho báo cáo.

## Chương 4. Thử nghiệm và đánh giá

### 4.1 Thiết lập thử nghiệm
#### 4.1.1 Hệ điều hành, compiler, Python
#### 4.1.2 Công cụ phân tích (readelf/objdump/ROPgadget)
#### 4.1.3 Cấu hình sysctl liên quan ASLR
> [NOTE chèn bảng cụ thể] **Bảng 4.1 - Môi trường thực nghiệm**  
> Điền từ máy chạy demo: `uname -a`, `python3 --version`, `gcc --version`, `ldd --version`, giá trị ASLR.

### 4.2 Quy trình thực hiện
#### 4.2.1 Build binaries
#### 4.2.2 Chạy `run_all_kali.sh` / `run_all_kali_quick.sh`
#### 4.2.3 Thu thập log và artifacts
> [NOTE chèn sơ đồ cụ thể] **Hình 4.1 - Quy trình chạy demo chuẩn**  
> Luồng đề xuất: `git pull` -> `make clean && make...` -> `run_all_kali.sh` -> `report_pack.sh`.

### 4.3 Kết quả thực hiện
#### 4.3.1 Kết quả chính
#### 4.3.2 Kết quả mở rộng
#### 4.3.3 Tổng hợp kết quả
> [NOTE chèn hình demo] Chèn 1–2 ảnh terminal tiêu biểu cho các trạng thái chính:  
> (i) thành công khi ASLR OFF (`uid=1337`), (ii) thất bại khi ASLR ON với địa chỉ cố định, (iii) thành công khi có leak bypass (`uid=1337`).  
> Ảnh lấy từ output của `run_all_full.log` hoặc `run_all_quick.log`.  
> [NOTE chèn bảng cụ thể] **Bảng 4.2 - Mitigation matrix**: 5 case (No protection, ASLR only, ASLR+leak, ASLR+NX, ASLR+NX+ROP).  
> Nguồn dữ liệu: output Step 7.

### 4.4 Phân tích số liệu
#### 4.4.1 Chỉ số hiệu quả
#### 4.4.2 Chỉ số ngẫu nhiên
#### 4.4.3 So sánh theo cấu hình
> [NOTE chèn hình/bảng] Chèn biểu đồ/bảng tương ứng với các chỉ số định lượng: success rate OFF/ON, histogram entropy địa chỉ stack, và so sánh PIE vs non-PIE.  
> Nguồn dữ liệu: `analysis/exploit_success_probability.png`, `analysis/entropy_histogram.png` và output của `analysis/compare_pie.py` (bảng địa chỉ `main`/`buffer`).

### 4.5 Đánh giá tổng hợp

#### 4.5.1 Mức độ hoàn thành
#### 4.5.2 Ý nghĩa kết quả
#### 4.5.3 Rủi ro và giới hạn
#### 4.5.4 Tồn tại hiện tại
> [NOTE chèn bảng cụ thể] Bảng đối chiếu mục tiêu và mức độ hoàn thành (có thể đặt tên **Bảng 4.4**).  
> Cột gợi ý: `Mục tiêu`, `Minh chứng`, `Kết quả`, `Mức độ hoàn thành`.
> [NOTE chèn hình] Defense-in-depth cho memory exploit (có thể là **Hình 4.x**): thể hiện lớp phòng thủ theo tầng (ASLR + NX + PIE + Canary + CFI/CET).  
> [NOTE chèn bảng cụ thể] Threats to validity (có thể là **Bảng 4.x**): `Nhóm threat`, `Mô tả`, `Ảnh hưởng`, `Biện pháp giảm thiểu`.  
> Nội dung tham chiếu: `docs/THREATS_TO_VALIDITY.md`.
- Tập trung user-space, không mở rộng sang kernel-space.
- ROP phụ thuộc mạnh vào runtime libc và gadget.
- Kết quả entropy phụ thuộc kiến trúc, kernel và loader.

## Chương 5. Kết luận và hướng phát triển

### 5.1 Kết luận
- Tổng hợp các kết quả thực nghiệm chính.
- Khẳng định vai trò của ASLR và giới hạn của nó.

### 5.2 Hướng phát triển
#### 5.2.1 Mở rộng sang heap overflow/UAF
#### 5.2.2 Đánh giá trên nhiều kiến trúc (x86-64, ARM64)
#### 5.2.3 Tích hợp bộ defense hiện đại (CET/CFI/PAC)
#### 5.2.4 Tự động hóa thống kê và báo cáo

## Tài liệu tham khảo
- Liệt kê theo chuẩn trích dẫn của khoa/bộ môn (IEEE/APA/Vancouver...).
- Ưu tiên tài liệu gốc: paper, man pages, tài liệu kernel, OWASP/CWE.

## Phụ lục

### Phụ lục A. Hướng dẫn chạy nhanh
- Tham chiếu: `docs/DEMO_COMMANDS_STANDARD.md`.

### Phụ lục B. Bảng cấu hình và phiên bản
- Tham chiếu: `environment_versions.txt.example` và artifact snapshot.

### Phụ lục C. Trích log quan trọng
- Phase 1/2/3 logs.
- Mitigation matrix.
- Success probability và entropy outputs.
