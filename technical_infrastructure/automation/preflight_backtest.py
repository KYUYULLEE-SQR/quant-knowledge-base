from __future__ import annotations

import argparse
import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger("preflight_backtest")


REQUIRED_RESULTS = [
    "results/trades.csv",
    "results/positions.csv",
    "results/nav.csv",
    "results/metrics.json",
    "results/reconciliation.csv",
]


SUSPICIOUS_SHARPE = 10.0


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def _read_csv_head(path: Path, n: int = 5) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, str]] = []
        for _, row in zip(range(n), reader, strict=False):
            rows.append(row)
        return (reader.fieldnames or []), rows


def _read_nav(path: Path, max_rows: int = 200000) -> list[float]:
    # Expect columns: timestamp-like + nav-equity-like. We accept many names.
    candidates = {"nav", "equity", "portfolio_value", "value"}
    values: list[float] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return values
        fieldset = {c.strip() for c in reader.fieldnames}
        nav_col = next((c for c in reader.fieldnames if c and c.strip().lower() in candidates), None)
        if nav_col is None:
            # fallback: second column
            cols = [c for c in reader.fieldnames if c]
            nav_col = cols[1] if len(cols) >= 2 else cols[0]
        if nav_col is None or nav_col not in fieldset and nav_col not in (reader.fieldnames or []):
            return values
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            raw = row.get(nav_col, "")
            try:
                values.append(float(raw))
            except Exception:
                continue
    return values


def _mdd(nav: list[float]) -> float | None:
    if len(nav) < 2:
        return None
    peak = nav[0]
    mdd = 0.0
    for x in nav:
        if x > peak:
            peak = x
        if peak > 0:
            dd = (x / peak) - 1.0
            if dd < mdd:
                mdd = dd
    return mdd


def check_required_files(experiment_dir: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for rel in REQUIRED_RESULTS:
        p = experiment_dir / rel
        results.append(
            CheckResult(
                name=f"required:{rel}",
                ok=p.exists() and p.is_file(),
                detail=str(p),
            )
        )
    return results


def check_nav_mtm(experiment_dir: Path) -> list[CheckResult]:
    nav_path = experiment_dir / "results/nav.csv"
    if not nav_path.exists():
        return [CheckResult("mtm:nav_exists", False, str(nav_path))]

    nav = _read_nav(nav_path)
    if len(nav) < 50:
        return [
            CheckResult("mtm:nav_length", False, f"nav rows={len(nav)} (too short; likely not MTM)"),
        ]

    mdd = _mdd(nav)
    if mdd is None:
        return [CheckResult("mtm:mdd", False, "cannot compute MDD")]

    # MDD exactly 0 is suspicious for trading strategies unless truly monotonic.
    if abs(mdd) < 1e-12:
        return [
            CheckResult("mtm:mdd_nonzero", False, "MDD=0 (suspicious: entry/exit-only NAV?)"),
        ]

    return [
        CheckResult("mtm:nav_length", True, f"nav rows={len(nav)}"),
        CheckResult("mtm:mdd", True, f"mdd={mdd:.4%}"),
    ]


def check_metrics_sanity(experiment_dir: Path) -> list[CheckResult]:
    metrics_path = experiment_dir / "results/metrics.json"
    if not metrics_path.exists():
        return [CheckResult("metrics:exists", False, str(metrics_path))]

    try:
        metrics: dict[str, Any] = json.loads(metrics_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [CheckResult("metrics:parse", False, f"json parse error: {e}")]

    # Accept flexible keys
    sharpe_key = next((k for k in metrics.keys() if k.lower() in {"sharpe", "sharpe_ratio"}), None)
    vol_key = next((k for k in metrics.keys() if k.lower() in {"vol", "volatility", "ann_vol"}), None)
    mdd_key = next((k for k in metrics.keys() if k.lower() in {"mdd", "max_drawdown"}), None)

    res: list[CheckResult] = [CheckResult("metrics:parse", True, f"keys={len(metrics)}")]

    def _get_float(k: str | None) -> float | None:
        if not k:
            return None
        try:
            return float(metrics[k])
        except Exception:
            return None

    sharpe = _get_float(sharpe_key)
    if sharpe is not None and abs(sharpe) > SUSPICIOUS_SHARPE:
        res.append(CheckResult("metrics:sharpe_range", False, f"sharpe={sharpe} (suspiciously large)"))
    else:
        res.append(CheckResult("metrics:sharpe_range", True, f"sharpe={sharpe}"))

    vol = _get_float(vol_key)
    if vol is not None and vol == 0.0 and sharpe is not None and sharpe != 0.0:
        res.append(CheckResult("metrics:vol_zero", False, f"vol=0 but sharpe={sharpe}"))
    else:
        res.append(CheckResult("metrics:vol_zero", True, f"vol={vol}"))

    mdd = _get_float(mdd_key)
    if mdd is not None and abs(mdd) < 1e-12:
        res.append(CheckResult("metrics:mdd_zero", False, "mdd=0 (suspicious)"))
    else:
        res.append(CheckResult("metrics:mdd_zero", True, f"mdd={mdd}"))

    return res


def write_report(experiment_dir: Path, checks: list[CheckResult]) -> Path:
    report = {
        "experiment_dir": str(experiment_dir),
        "ok": all(c.ok for c in checks),
        "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in checks],
    }
    out_path = experiment_dir / "results" / "preflight_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


def main() -> int:
    _configure_logging()
    parser = argparse.ArgumentParser(description="Backtest preflight: artifacts + MTM/metrics sanity.")
    parser.add_argument("experiment_dir", type=Path, help="Path to an experiment folder containing results/")
    args = parser.parse_args()

    exp_dir = args.experiment_dir.expanduser().resolve()
    if not exp_dir.exists() or not exp_dir.is_dir():
        LOGGER.error("Invalid experiment_dir: %s", exp_dir)
        return 1

    checks: list[CheckResult] = []
    checks.extend(check_required_files(exp_dir))
    checks.extend(check_nav_mtm(exp_dir))
    checks.extend(check_metrics_sanity(exp_dir))

    ok = all(c.ok for c in checks)
    for c in checks:
        level = logging.INFO if c.ok else logging.WARNING
        LOGGER.log(level, "%s | %s | %s", "OK" if c.ok else "FAIL", c.name, c.detail)

    report_path = write_report(exp_dir, checks)
    LOGGER.info("Wrote report: %s", report_path)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())


