"""Command-line generator for The Museum of Lost Hours."""

from __future__ import annotations

import argparse
from pathlib import Path

from engine import write_instance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_instance(args.output, args.seed)
    print(f"Wrote museum instance to {args.output}")


if __name__ == "__main__":
    main()

