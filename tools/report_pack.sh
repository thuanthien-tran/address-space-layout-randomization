#!/usr/bin/env bash
set -euo pipefail

# Collect reproducibility artifacts into artifacts/<timestamp>/

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="$ROOT_DIR/artifacts/$TS"
AN_DIR="$ROOT_DIR/analysis"

mkdir -p "$OUT_DIR"
mkdir -p "$OUT_DIR/analysis"

copy_if_exists() {
  local src="$1"
  local dst="$2"
  if [[ -f "$src" ]]; then
    cp "$src" "$dst"
  fi
}

echo "[INFO] Packing artifacts to: $OUT_DIR"

copy_if_exists "$ROOT_DIR/full_demo.log" "$OUT_DIR/full_demo.log"
copy_if_exists "$ROOT_DIR/run_all_quick.log" "$OUT_DIR/run_all_quick.log"
copy_if_exists "$AN_DIR/stack_addresses.csv" "$OUT_DIR/analysis/stack_addresses.csv"
copy_if_exists "$AN_DIR/entropy_histogram.png" "$OUT_DIR/analysis/entropy_histogram.png"
copy_if_exists "$AN_DIR/exploit_success_probability.png" "$OUT_DIR/analysis/exploit_success_probability.png"

cp "$ROOT_DIR/README.md" "$OUT_DIR/README.md"
cp "$ROOT_DIR/REPRODUCIBILITY.md" "$OUT_DIR/REPRODUCIBILITY.md"
cp "$ROOT_DIR/EVALUATION_METRICS.md" "$OUT_DIR/EVALUATION_METRICS.md"
cp "$ROOT_DIR/THREAT_MODEL.md" "$OUT_DIR/THREAT_MODEL.md"
cp "$ROOT_DIR/DEFENSE.md" "$OUT_DIR/DEFENSE.md"
cp "$ROOT_DIR/docs/ASSUMPTIONS_AND_LIMITATIONS.md" "$OUT_DIR/ASSUMPTIONS_AND_LIMITATIONS.md"
copy_if_exists "$ROOT_DIR/docs/THREATS_TO_VALIDITY.md" "$OUT_DIR/THREATS_TO_VALIDITY.md"
copy_if_exists "$ROOT_DIR/docs/CONCLUSION_AND_FUTURE_WORK.md" "$OUT_DIR/CONCLUSION_AND_FUTURE_WORK.md"

{
  echo "timestamp=$TS"
  echo "uname=$(uname -a 2>/dev/null || true)"
  echo "python=$(python3 --version 2>/dev/null || true)"
  echo "gcc=$(gcc --version 2>/dev/null | head -n 1 || true)"
  echo "aslr=$(cat /proc/sys/kernel/randomize_va_space 2>/dev/null || true)"
  echo "glibc=$(ldd --version 2>/dev/null | head -n 1 || true)"
} > "$OUT_DIR/environment_snapshot.txt"

echo "[INFO] Done. Folder: $OUT_DIR"
