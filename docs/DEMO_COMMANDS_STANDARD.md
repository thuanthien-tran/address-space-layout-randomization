# Demo Commands (Standard)

Muc tieu: chay demo on dinh, co log day du de quay video va chen bao cao.

## 1) Chay full demo (khuyen nghi khi quay)

```bash
cd "$HOME/Address Space Layout Randomization"

# Dong bo code moi nhat
git fetch origin
git reset --hard origin/main

# Quyen thuc thi script
chmod +x run_all_kali.sh run_all_kali_quick.sh demo_aslr/get_fixed_addr.sh tools/report_pack.sh

# Build sach
cd demo_aslr
make clean && make && make pie && make nx
cd ..

# Chay full (khong pause)
SKIP_PAUSE=1 ./run_all_kali.sh | tee run_all_full.log
```

## 2) Chay quick demo (kiem tra nhanh truoc khi quay)

```bash
cd "$HOME/Address Space Layout Randomization"
SKIP_PAUSE=1 ./run_all_kali_quick.sh | tee run_all_quick.log
```

## 3) Gom artifacts cho bao cao

```bash
cd "$HOME/Address Space Layout Randomization"
bash tools/report_pack.sh
```

## 4) Checklist output dung (de xac nhan demo OK)

- Phase1: thay `uid=1337`.
- Phase2 (ASLR ON + fixed addr): success ~0%.
- Phase3 (ASLR ON + leak): thay `uid=1337`.
- Entropy: co file `analysis/stack_addresses.csv`.
- PIE compare: `main` non-PIE co dinh, PIE thay doi.
- ROP Phase4 co the fail tuy moi truong (chap nhan neu da note trong bao cao).

## 5) Neu gap loi quyen/chua co binary

```bash
cd "$HOME/Address Space Layout Randomization"
chmod +x run_all_kali.sh run_all_kali_quick.sh demo_aslr/get_fixed_addr.sh tools/report_pack.sh
cd demo_aslr && make clean && make && make pie && make nx && cd ..
```

