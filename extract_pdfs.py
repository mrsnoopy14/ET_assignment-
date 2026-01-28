from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        parts.append(f"\n\n--- Page {i} ---\n")
        parts.append(text)
    return "".join(parts).strip()


def main() -> int:
    root = Path(__file__).resolve().parent
    pdfs = [
        root / "1. ET_Assessment_CSE.pdf",
        root / "2. Thermal_Reference.pdf",
    ]

    out_dir = root / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    for pdf in pdfs:
        if not pdf.exists():
            print(f"Missing: {pdf}")
            continue
        text = extract_pdf_text(pdf)
        out_path = out_dir / (pdf.stem + ".txt")
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path} ({len(text):,} chars)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
