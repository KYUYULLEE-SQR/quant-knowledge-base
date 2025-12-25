from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


LOGGER = logging.getLogger("bootstrap_project_state")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def _read_template(template_path: Path) -> str:
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def _atomic_write_text(target_path: Path, content: str) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, dir=str(target_path.parent), encoding="utf-8") as tmp:
        tmp.write(content)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name
    os.replace(tmp_name, target_path)


def _create_if_missing(target_path: Path, content: str) -> bool:
    if target_path.exists():
        LOGGER.info("Exists, skip: %s", target_path)
        return False
    _atomic_write_text(target_path, content)
    LOGGER.info("Created: %s", target_path)
    return True


def bootstrap(project_root: Path, meta_root: Path) -> int:
    if not project_root.exists() or not project_root.is_dir():
        raise NotADirectoryError(f"Invalid project root: {project_root}")

    templates_dir = meta_root / "templates"
    rules_template = _read_template(templates_dir / "PROJECT_RULES.md")
    state_template = _read_template(templates_dir / "STATE.md")

    created_any = False
    created_any |= _create_if_missing(project_root / "PROJECT_RULES.md", rules_template)
    created_any |= _create_if_missing(project_root / "STATE.md", state_template)

    if not created_any:
        LOGGER.info("No changes needed.")
    return 0


def main() -> int:
    _configure_logging()
    parser = argparse.ArgumentParser(
        description="Initialize per-project PROJECT_RULES.md and STATE.md (creates only if missing)."
    )
    parser.add_argument(
        "project_root",
        type=Path,
        help="Absolute path to project root (e.g., /home/sqr/options_trading)",
    )
    parser.add_argument(
        "--meta-root",
        type=Path,
        default=Path("/home/sqr/_meta"),
        help="Meta root containing templates/ (default: /home/sqr/_meta)",
    )
    args = parser.parse_args()

    try:
        return bootstrap(args.project_root.expanduser().resolve(), args.meta_root.expanduser().resolve())
    except Exception:
        LOGGER.exception("Bootstrap failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


