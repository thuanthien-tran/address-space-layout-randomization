#!/usr/bin/env bash
set -euo pipefail

# One-shot demo runner for Kali/Ubuntu VM.
# It guides you through:
# 1) build
# 2) phase1/2/3/4
# 3) mitigation matrix
# 4) entropy + probability + pie comparison
#
# Nếu sau Phase1 màn hình "đứng im": script đang CHỜ BẠN NHẤN ENTER (không phải treo).
# Chạy không tạm dừng: SKIP_PAUSE=1 ./run_all_kali.sh
# Trên Linux dùng LF (không CRLF): dos2unix run_all_kali.sh

export PYTHONUNBUFFERED=1

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$ROOT_DIR/demo_aslr"
EXP_DIR="$ROOT_DIR/exploits"
AN_DIR="$ROOT_DIR/analysis"
SKIP_PAUSE="${SKIP_PAUSE:-0}"

info() { echo -e "\n[INFO] $*"; }
warn() { echo -e "\n[WARN] $*"; }
die() { echo -e "\n[ERROR] $*"; exit 1; }

# Chờ Enter trừ khi SKIP_PAUSE=1 (máy yếu / chạy batch)
pause_enter() {
  local msg="${1:-Tiep tuc}"
  if [[ "${SKIP_PAUSE}" == "1" ]]; then
    echo "[skip pause] ${msg}"
    return 0
  fi
  echo ""
  echo "=========================================="
  echo "  NHAN ENTER de tiep tuc (khong phai treo)"
  echo "  ${msg}"
  echo "=========================================="
  read -r _
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    warn "Missing command: $1"
    return 1
  fi
  return 0
}

info "Project root: $ROOT_DIR"
require_cmd gcc || true
require_cmd python3 || true
require_cmd make || true

info "Step 0: Optional dependency check"
if ! command -v ROPgadget >/dev/null 2>&1; then
  warn "ROPgadget not found. Install with: pip3 install --user ROPGadget"
fi

if ! python3 -c "import matplotlib" >/dev/null 2>&1; then
  warn "matplotlib not found. Install with: pip3 install --user matplotlib"
fi

info "Step 1: Build all required binaries"
cd "$DEMO_DIR"
make
make pie
make nx

info "Step 2: Phase1 (ASLR OFF, shellcode success)"
sudo sysctl -w kernel.randomize_va_space=0
PH1_OUT="$(python3 "$EXP_DIR/exploit_phase1_aslr_off.py" 2>&1 || true)"
echo "$PH1_OUT"
if ! echo "$PH1_OUT" | grep -Eq 'uid=[0-9]+'; then
  die "Phase1 không thấy marker uid=. Kiểm tra exploits/exploit_config.py (shellcode marker) và build demo_aslr."
fi
pause_enter "Sau Phase1 — buoc tiep: lay dia chi co dinh (get_fixed_addr)"

info "Step 3: Capture fixed address while ASLR OFF"
FIXED_LINE="$(./get_fixed_addr.sh | tee /tmp/aslr_fixed_addr.log | grep -i 'Address of buffer' || true)"
if [[ -z "${FIXED_LINE}" ]]; then
  warn "Could not auto-detect fixed addr. Please run ./get_fixed_addr.sh manually."
  if [[ "${SKIP_PAUSE}" == "1" ]]; then
    warn "SKIP_PAUSE=1 and no fixed line — set FIXED_ADDR manually or run get_fixed_addr.sh"
    FIXED_ADDR="${FIXED_ADDR:-}"
  else
    read -r -p "Nhap fixed addr (vd 0x7ff...): " FIXED_ADDR
  fi
else
  FIXED_ADDR="$(echo "$FIXED_LINE" | sed -E 's/.*(0x[0-9a-fA-F]+).*/\1/')"
fi
info "Fixed address for phase2: ${FIXED_ADDR:-<none>}"

info "Step 4: Phase2 (ASLR ON, fixed address expected fail)"
sudo sysctl -w kernel.randomize_va_space=2
if [[ -n "${FIXED_ADDR:-}" ]]; then
  python3 "$EXP_DIR/exploit_phase2_aslr_on_fail.py" --fixed-addr "$FIXED_ADDR" --runs 50 || true
else
  warn "Skip phase2 auto-run because FIXED_ADDR missing."
fi
pause_enter "Sau Phase2"

info "Step 5: Phase3 (ASLR ON + leak bypass)"
PH3_OUT="$(python3 "$EXP_DIR/exploit_phase3_bypass_leak.py" 2>&1 || true)"
echo "$PH3_OUT"
if ! echo "$PH3_OUT" | grep -Eq 'uid=[0-9]+'; then
  die "Phase3 không thấy marker uid=. Bypass leak chưa thành công; không tiếp tục để tránh số liệu sai."
fi
pause_enter "Sau Phase3"

info "Step 6: Phase4 (ASLR ON + NX + ROP ret2libc)"
python3 "$EXP_DIR/exploit_phase4_rop.py" || true
pause_enter "Sau Phase4"

info "Step 7: Mitigation matrix table"
if [[ -n "${FIXED_ADDR:-}" ]]; then
  python3 "$AN_DIR/mitigation_matrix.py" --fixed-addr "$FIXED_ADDR" --non-interactive --auto-sysctl || true
else
  python3 "$AN_DIR/mitigation_matrix.py" || true
fi
pause_enter "Sau mitigation matrix"

info "Step 8: Exploit success probability model (OFF vs ON)"
sudo sysctl -w kernel.randomize_va_space=0
python3 "$AN_DIR/exploit_success_probability.py" --phase off --runs 200 || true
if [[ -n "${FIXED_ADDR:-}" ]]; then
  sudo sysctl -w kernel.randomize_va_space=2
  python3 "$AN_DIR/exploit_success_probability.py" --phase on --runs 200 --fixed-addr "$FIXED_ADDR" || true
else
  warn "No fixed addr available, skip phase on probability run."
fi
pause_enter "Sau probability"

info "Step 9: Entropy measurement (with CI)"
sudo sysctl -w kernel.randomize_va_space=2
python3 "$AN_DIR/entropy_measurement.py" --runs 500 --ci 500 || true

info "Step 10: PIE comparison"
python3 "$AN_DIR/compare_pie.py" --runs 5 || true

info "DONE. Artifacts to use in report:"
echo " - $AN_DIR/stack_addresses.csv"
echo " - $AN_DIR/entropy_histogram.png (if matplotlib installed)"
echo " - $AN_DIR/exploit_success_probability.png (if matplotlib installed)"
echo " - terminal outputs from phases 1-4 and mitigation matrix"
