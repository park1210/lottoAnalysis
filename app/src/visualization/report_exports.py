from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import FIGURES_DIR, TABLES_DIR


def save_report_figure(
    fig,
    filename: str,
    *,
    subdir: str | None = None,
    dpi: int = 200,
    bbox_inches: str = "tight",
) -> Path:
    output_dir = FIGURES_DIR / subdir if subdir else FIGURES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    fig.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
    return output_path


def save_report_table(
    df: pd.DataFrame,
    filename: str,
    *,
    subdir: str | None = None,
    index: bool = False,
    encoding: str = "utf-8-sig",
) -> Path:
    output_dir = TABLES_DIR / subdir if subdir else TABLES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    suffix = output_path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(output_path, index=index, encoding=encoding)
    elif suffix in {".xlsx", ".xls"}:
        df.to_excel(output_path, index=index)
    elif suffix == ".md":
        output_path.write_text(df.to_markdown(index=index), encoding="utf-8")
    else:
        raise ValueError("filename must end with .csv, .xlsx, .xls, or .md")

    return output_path
