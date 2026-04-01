from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    src_root = project_root / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))
    from common.harness.cli import main as harness_main

    return harness_main()


if __name__ == "__main__":
    raise SystemExit(main())
