from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import formulas


def main() -> int:
    xlsx = Path("3. Heat_Sink_Design_Ref.xlsx")
    if not xlsx.exists():
        raise SystemExit(f"Missing: {xlsx}")

    # Load workbook with formula evaluation.
    excel_model = formulas.ExcelModel().loads(str(xlsx)).finish()

    # Calculate all cells.
    results = excel_model.calculate()

    # Flatten results into {sheet!A1: value}
    flat: dict[str, Any] = {}
    for addr, value in results.items():
        # addr looks like "Sheet1!A1" already
        flat[str(addr)] = value

    # Keep only scalar numbers/strings for easy search.
    filtered: dict[str, Any] = {}
    for k, v in flat.items():
        if isinstance(v, (int, float, str)):
            filtered[k] = v

    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "excel_calculated.json"
    out_path.write_text(json.dumps(filtered, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_path} with {len(filtered)} entries")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
