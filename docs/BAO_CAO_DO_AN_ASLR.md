# BAO CAO DO AN

## De tai
Phan tich hieu qua Address Space Layout Randomization (ASLR) trong ngan chan khai thac Buffer Overflow.

## Chuong 1. Tong quan de tai

### 1.1 Ly do chon de tai
- Buffer overflow la nhom loi kinh dien, co tinh thuc tien cao trong ATHT.
- ASLR la co che phong thu cot loi tren he dieu hanh hien dai.
- Do an cho phep ket hop ly thuyet, khai thac, va danh gia dinh luong.

### 1.2 Muc tieu nghien cuu
- Chung minh kha nang khai thac khi ASLR tat.
- Chung minh exploit dia chi co dinh that bai khi ASLR bat.
- Trinh bay ky thuat bypass ASLR bang information leak.
- Danh gia dinh luong bang success rate, entropy, va so sanh PIE/non-PIE.

### 1.3 Doi tuong va pham vi
- Doi tuong: chuong trinh C co loi stack buffer overflow.
- Pham vi: user-space tren Linux x86-64, khong di sau KASLR/kernel exploit.
- Mitigations xem xet: ASLR, NX, PIE; minh hoa ROP ret2libc.

### 1.4 Cau hoi nghien cuu
- ASLR lam giam xac suat exploit theo cach nao?
- Information leak anh huong den hieu qua ASLR ra sao?
- PIE bo sung gi cho ASLR trong boi canh khai thac?

### 1.5 Dong gop chinh cua do an
- Xay dung bo demo 5 giai doan co the tai lap.
- Bo script tu dong hoa run-to-report.
- Bo tieu chi danh gia va tai lieu hoa threats/limitations.

## Chuong 2. Co so ly thuyet

### 2.1 Tong quan bo nho tien trinh
#### 2.1.1 Vung executable
#### 2.1.2 Vung stack
#### 2.1.3 Vung heap
#### 2.1.4 Thu vien dung (shared libraries)

### 2.2 Buffer Overflow tren stack
#### 2.2.1 Co che ghi de return address
#### 2.2.2 Vai tro cua offset va stack frame
#### 2.2.3 Dieu kien de khai thac thanh cong

### 2.3 Co che ASLR
#### 2.3.1 Nguyen ly random hoa dia chi
#### 2.3.2 randomize_va_space (0/1/2)
#### 2.3.3 Entropy va y nghia bao mat

### 2.4 Cac co che bo tro
#### 2.4.1 NX (Non-Executable stack)
#### 2.4.2 PIE (Position Independent Executable)
#### 2.4.3 ROP/ret2libc va vai tro gadget

### 2.5 Han che cua ASLR
#### 2.5.1 Information leak
#### 2.5.2 Brute-force trong boi canh thuc te
#### 2.5.3 Su can thiet cua defense in depth

## Chuong 3. Phan tich va thiet ke he thong demo

### 3.1 Kien truc du an
#### 3.1.1 Thanh phan demo_aslr
#### 3.1.2 Thanh phan exploits
#### 3.1.3 Thanh phan analysis
#### 3.1.4 Thanh phan docs/tools

### 3.2 Thiet ke chuong trinh de bi tan cong
#### 3.2.1 aslr_demo.c va ham vuln()
#### 3.2.2 Cac thong so build (no-pie, execstack, nx)
#### 3.2.3 Luong in leak dia chi (main/printf/buffer/heap)

### 3.3 Thiet ke exploit theo giai doan
#### 3.3.1 Giai doan 1: ASLR OFF (shellcode success)
#### 3.3.2 Giai doan 2: ASLR ON + fixed address (expected fail)
#### 3.3.3 Giai doan 3: ASLR ON + leak bypass
#### 3.3.4 Giai doan 4: NX + ASLR + ROP ret2libc
#### 3.3.5 Giai doan 5: So sanh PIE vs non-PIE

### 3.4 Cau hinh va tham so quan trong
#### 3.4.1 OFFSET_RET va RET_DELTA
#### 3.4.2 Shellcode marker uid=1337
#### 3.4.3 Dieu kien moi truong de tai lap

## Chuong 4. Cai dat va thuc nghiem

### 4.1 Moi truong thuc nghiem
#### 4.1.1 He dieu hanh, compiler, python
#### 4.1.2 Cong cu phan tich (readelf/objdump/ROPgadget)
#### 4.1.3 Cau hinh sysctl lien quan ASLR

### 4.2 Quy trinh chay demo chuan
#### 4.2.1 Build binaries
#### 4.2.2 Chay run_all_kali.sh / run_all_kali_quick.sh
#### 4.2.3 Thu thap log va artifacts

### 4.3 Ket qua giai doan khai thac
#### 4.3.1 Ket qua Phase1, Phase2, Phase3
#### 4.3.2 Ket qua Phase4 (ROP) va phan tich
#### 4.3.3 Bang mitigation matrix

### 4.4 Ket qua dinh luong
#### 4.4.1 Exploit success probability (OFF vs ON)
#### 4.4.2 Entropy do tu du lieu stack address
#### 4.4.3 PIE comparison ket hop ASLR

## Chuong 5. Danh gia va thao luan

### 5.1 Danh gia theo muc tieu de tai
#### 5.1.1 Muc tieu dat duoc
#### 5.1.2 Muc tieu chua dat hoac dat mot phan

### 5.2 Phan tich y nghia bao mat
#### 5.2.1 ASLR giam xac suat khai thac
#### 5.2.2 Info leak lam suy yeu ASLR
#### 5.2.3 ASLR can ket hop NX, PIE, canary, CFI

### 5.3 Threats to validity
#### 5.3.1 Internal validity
#### 5.3.2 Construct validity
#### 5.3.3 External validity
#### 5.3.4 Statistical conclusion validity

### 5.4 Han che he thong demo
- Tap trung user-space, khong mo rong sang kernel-space.
- ROP phu thuoc manh vao runtime libc va gadget.
- Ket qua entropy phu thuoc kien truc, kernel, loader.

## Chuong 6. Ket luan va huong phat trien

### 6.1 Ket luan
- Tong hop cac ket qua thuc nghiem chinh.
- Khang dinh vai tro cua ASLR va gioi han cua no.

### 6.2 Huong phat trien
#### 6.2.1 Mo rong sang heap overflow/UAF
#### 6.2.2 Danh gia tren nhieu kien truc (x86-64, ARM64)
#### 6.2.3 Tich hop bo defense hien dai (CET/CFI/PAC)
#### 6.2.4 Tu dong hoa thong ke va bao cao

## Tai lieu tham khao
- Liet ke theo chuan trich dan cua khoa/bo mon (IEEE/APA/Vancouver...).
- Uu tien tai lieu goc: paper, man pages, tai lieu kernel, OWASP/CWE.

## Phu luc

### Phu luc A. Huong dan chay nhanh
- Tham chieu: `docs/DEMO_COMMANDS_STANDARD.md`.

### Phu luc B. Bang cau hinh va versions
- Tham chieu: `environment_versions.txt.example` va artifact snapshot.

### Phu luc C. Trich log quan trong
- Phase1/2/3 logs.
- Mitigation matrix.
- Success probability va entropy outputs.
