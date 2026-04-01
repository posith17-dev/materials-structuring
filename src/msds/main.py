from __future__ import annotations

from pathlib import Path

from .extractor import parse_msds_records
from .parser import extract_text
from .reporter import write_outputs


def process_file(path: str | Path, out_dir: str | Path) -> dict[str, Path]:
    source = Path(path)
    text = extract_text(source)
    records = parse_msds_records(text)
    return write_outputs(out_dir, source.name, records)
