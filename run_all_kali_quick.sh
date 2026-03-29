#!/usr/bin/env bash
set -euo pipefail

# Quick runner for low-resource VMs.
# Research note: success marker is regex `uid=\d+` (e.g., uid=1337).

export PYTHONUNBUFFERED=1

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$ROOT_DIR/demo_aslr"
EXP_DIR="$ROOT_DIR/exploits"
AN_DIR="$ROOT_DIR/analysis"
SKIP_PAUSE="${SKIP_PAUSE:-1}"

info() { echo -e "\n[INFO] $*"; }
warn() { echo -e "\n[WARN] $*"; }
die() { echo -e "\n[ERROR] $*"; exit 1; }

pause_enter() {
  local msg="${1:-Tiep tuc}"
  if [[ "${SKIP_PAUSE}" == "1" ]]; then
    echo "[skip pause] ${msg}"
    return 0
  fi
  read -r -p "${msg} (Enter) " _
}

info "Project root: $ROOT_DIR"

info "Step 1: Build binaries"
cd "$DEMO_DIR"
make
make pie
make nx

info "Step 2: Phase1 (ASLR OFF)"
sudo sysctl -w kernel.randomize_va_space=0
PH1_OUT="$(python3 "$EXP_DIR/exploit_phase1_aslr_off.py" 2>&1 || true)"
echo "$PH1_OUT"
if ! echo "$PH1_OUT" | grep -Eq 'uid=[0-9]+'; then
  die "Phase1 không thấy marker uid=. Kiểm tra exploits/exploit_config.py (shellcode marker) và build demo_aslr."
fi

info "Step 3: Capture fixed address"
FIXED_LINE="$(./get_fixed_addr.sh | grep -i 'Address of buffer' || true)"
if [[ -n "${FIXED_LINE}" ]]; then
  FIXED_ADDR="$(echo "$FIXED_LINE" | sed -E 's/.*(0x[0-9a-fA-F]+).*/\1/')"
else
  warn "Could not auto-detect fixed addr. Set FIXED_ADDR env or enter manually."
  if [[ -n "${FIXED_ADDR:-}" ]]; then
    true
  elif [[ "${SKIP_PAUSE}" == "1" ]]; then
    FIXED_ADDR=""
  else
    read -r -p "Nhap fixed addr (vd 0x7ff...): " FIXED_ADDR
  fi
fi
info "Fixed address: ${FIXED_ADDR:-<none>}"

info "Step 4: Phase2 (ASLR ON fixed-address expected fail)"
sudo sysctl -w kernel.randomize_va_space=2
if [[ -n "${FIXED_ADDR:-}" ]]; then
  python3 "$EXP_DIR/exploit_phase2_aslr_on_fail.py" --fixed-addr "$FIXED_ADDR" --runs 20 || true
else
  warn "Skip phase2 (no fixed addr)."
fi

info "Step 5: Phase3 (ASLR ON + leak)"
PH3_OUT="$(python3 "$EXP_DIR/exploit_phase3_bypass_leak.py" 2>&1 || true)"
echo "$PH3_OUT"
if ! echo "$PH3_OUT" | grep -Eq 'uid=[0-9]+'; then
  die "Phase3 không thấy marker uid=. Bypass leak chưa thành công; không tiếp tục để tránh số liệu sai."
fi

info "Step 6: Phase4 (ASLR ON + NX + ROP)"
python3 "$EXP_DIR/exploit_phase4_rop.py" || true

info "Step 7: Mitigation matrix"
if [[ -n "${FIXED_ADDR:-}" ]]; then
  python3 "$AN_DIR/mitigation_matrix.py" --fixed-addr "$FIXED_ADDR" --non-interactive --auto-sysctl || true
else
  python3 "$AN_DIR/mitigation_matrix.py" || true
fi

info "Step 8: Probability quick run"
sudo sysctl -w kernel.randomize_va_space=0
python3 "$AN_DIR/exploit_success_probability.py" --phase off --runs 50 --no-plot || true
if [[ -n "${FIXED_ADDR:-}" ]]; then
  sudo sysctl -w kernel.randomize_va_space=2
  python3 "$AN_DIR/exploit_success_probability.py" --phase on --runs 50 --fixed-addr "$FIXED_ADDR" --no-plot || true
fi

info "Step 9: Entropy quick run"
sudo sysctl -w kernel.randomize_va_space=2
python3 "$AN_DIR/entropy_measurement.py" --runs 100 --ci 100 --no-plot || true

info "Step 10: PIE quick comparison"
python3 "$AN_DIR/compare_pie.py" --runs 3 || true

info "DONE (quick mode)."
echo "Artifacts:"
echo " - $AN_DIR/stack_addresses.csv"
echo " - terminal output/logs"
