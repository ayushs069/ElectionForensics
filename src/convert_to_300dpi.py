"""
convert_to_300dpi.py
--------------------
Converts all project plot PNGs to 300 DPI and saves them under
  PRJ-3/300dpi/
preserving the exact sub-folder structure from the original locations.

Source plot directories:
  EDA/plots/ed1/
  EDA/plots/ed2/
  INDIA/rvm_outputs/eda/
  INDIA/rvm_outputs/per_state/
  INDIA/rvm_outputs/pooled/
  INDIA/rvm_outputs/fraud_barchart.png
  INDIA/rvm_outputs_14states/eda/
  INDIA/rvm_outputs_14states/per_state/
  INDIA/rvm_outputs_14states/pooled/
  INDIA/rvm_outputs_14states/fraud_barchart.png
  WORLD VS INDIA/plots/
  rvm_outputs/per_country/
  rvm_outputs/pooled/
  rvm_outputs/fraud_barchart.png
"""

import os
import shutil
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(r"C:\Users\shubham\Desktop\PRJ-3")
OUT_ROOT = ROOT / "300dpi"
TARGET_DPI = (300, 300)

# ── Define every source path to process ──────────────────────────────────────
# Each entry is either a FILE or a DIRECTORY that will be walked recursively.
SOURCES = [
    # EDA
    ROOT / "EDA" / "plots" / "ed1",
    ROOT / "EDA" / "plots" / "ed2",

    # INDIA – rvm_outputs
    ROOT / "INDIA" / "rvm_outputs" / "eda",
    ROOT / "INDIA" / "rvm_outputs" / "per_state",
    ROOT / "INDIA" / "rvm_outputs" / "pooled",
    ROOT / "INDIA" / "rvm_outputs" / "fraud_barchart.png",

    # INDIA – rvm_outputs_14states
    ROOT / "INDIA" / "rvm_outputs_14states" / "eda",
    ROOT / "INDIA" / "rvm_outputs_14states" / "per_state",
    ROOT / "INDIA" / "rvm_outputs_14states" / "pooled",
    ROOT / "INDIA" / "rvm_outputs_14states" / "fraud_barchart.png",

    # WORLD VS INDIA
    ROOT / "WORLD VS INDIA" / "plots",

    # World rvm_outputs
    ROOT / "rvm_outputs" / "per_country",
    ROOT / "rvm_outputs" / "pooled",
    ROOT / "rvm_outputs" / "fraud_barchart.png",
]


def convert_png(src: Path, dst: Path) -> None:
    """Open a PNG, set DPI metadata to 300, save to dst."""
    with Image.open(src) as img:
        # Convert to RGB if needed (some PNGs have transparency)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        dst.parent.mkdir(parents=True, exist_ok=True)
        img.save(dst, dpi=TARGET_DPI, format="PNG", optimize=False)


def process_source(source: Path) -> list[str]:
    """Process a file or directory source. Returns list of processed file paths."""
    processed = []
    if not source.exists():
        print(f"  [SKIP – not found] {source}")
        return processed

    if source.is_file():
        if source.suffix.lower() == ".png":
            rel = source.relative_to(ROOT)
            dst = OUT_ROOT / rel
            convert_png(source, dst)
            print(f"  [OK] {rel}")
            processed.append(str(rel))
    else:
        # Walk the directory
        for png in sorted(source.rglob("*.png")):
            rel = png.relative_to(ROOT)
            dst = OUT_ROOT / rel
            convert_png(png, dst)
            print(f"  [OK] {rel}")
            processed.append(str(rel))

    return processed


def main():
    print(f"\n{'='*60}")
    print(f"  Converting all plots to 300 DPI")
    print(f"  Output root: {OUT_ROOT}")
    print(f"{'='*60}\n")

    total = 0
    for source in SOURCES:
        print(f"\nProcessing: {source.relative_to(ROOT)}")
        done = process_source(source)
        total += len(done)

    print(f"\n{'='*60}")
    print(f"  Done! {total} PNG(s) converted to 300 DPI.")
    print(f"  All files saved under: {OUT_ROOT}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
