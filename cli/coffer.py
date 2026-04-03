#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Install PyYAML: pip install pyyaml") from exc


ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = ROOT / "config" / "coffer.yaml"

INCOME_PATH = ROOT / "ledger" / "income.yaml"
EXPENSE_PATH = ROOT / "ledger" / "expenses.yaml"
RESERVE_PATH = ROOT / "ledger" / "reserves.yaml"

EXPORT_DIR = ROOT / "exports"
EXPORT_PATH = EXPORT_DIR / "coffer_status.json"


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_yaml(path: Path):
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text())
    return data or {}


def save_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def load_config():
    return load_yaml(CONFIG_PATH)


def load_income():
    return load_yaml(INCOME_PATH).get("income", [])


def load_expenses():
    return load_yaml(EXPENSE_PATH).get("expenses", [])


def load_reserves():
    return load_yaml(RESERVE_PATH).get("reserves", {}).get("snapshots", [])


def save_income(rows):
    save_yaml(INCOME_PATH, {"income": rows})


def save_expenses(rows):
    save_yaml(EXPENSE_PATH, {"expenses": rows})


def save_reserves(rows):
    save_yaml(RESERVE_PATH, {"reserves": {"snapshots": rows}})


def total(rows):
    return round(sum(float(x.get("amount", 0)) for x in rows), 2)


def totals():
    inc = total(load_income())
    exp = total(load_expenses())
    bal = round(inc - exp, 2)

    return {"income": inc, "expenses": exp, "balance": bal}


def allocation(balance, buckets):
    out = []

    for name, pct in buckets.items():
        pct = float(pct)
        amount = round(balance * (pct / 100), 2)

        out.append(
            {
                "bucket": name,
                "percent": pct,
                "amount": amount,
            }
        )

    return out


def export_payload():
    config = load_config()
    inc = load_income()
    exp = load_expenses()
    res = load_reserves()

    t = totals()

    buckets = config.get("allocation_buckets", {})

    return {
        "generated_at": now(),
        "config": config,
        "totals": t,
        "allocation_preview": allocation(t["balance"], buckets),
        "income": inc,
        "expenses": exp,
        "reserves": res,
    }


def command_status(_):

    t = totals()

    print("==================================")
    print("         AKASHA COFFER")
    print("==================================")

    print(f"Income:  {t['income']:.2f}")
    print(f"Expense: {t['expenses']:.2f}")
    print(f"Balance: {t['balance']:.2f}")


def command_add_income(args):

    rows = load_income()

    entry = {
        "timestamp": now(),
        "source": args.source,
        "amount": round(float(args.amount), 2),
        "currency": args.currency,
        "note": args.note,
    }

    rows.append(entry)

    save_income(rows)

    print(json.dumps(entry, indent=2))


def command_add_expense(args):

    rows = load_expenses()

    entry = {
        "timestamp": now(),
        "category": args.category,
        "amount": round(float(args.amount), 2),
        "currency": args.currency,
        "note": args.note,
    }

    rows.append(entry)

    save_expenses(rows)

    print(json.dumps(entry, indent=2))


def command_snapshot(args):

    t = totals()

    rows = load_reserves()

    entry = {
        "timestamp": now(),
        "label": args.label,
        "balance": t["balance"],
        "note": args.note,
    }

    rows.append(entry)

    save_reserves(rows)

    print(json.dumps(entry, indent=2))


def command_export(_):

    payload = export_payload()

    EXPORT_DIR.mkdir(exist_ok=True)

    EXPORT_PATH.write_text(json.dumps(payload, indent=2))

    print("Export written:", EXPORT_PATH)


def command_watch(_):

    print("Watching ledger files...")
    print("Press Ctrl+C to stop.\n")

    last = 0

    while True:

        newest = max(
            INCOME_PATH.stat().st_mtime,
            EXPENSE_PATH.stat().st_mtime,
            RESERVE_PATH.stat().st_mtime,
        )

        if newest > last:

            payload = export_payload()

            EXPORT_DIR.mkdir(exist_ok=True)

            EXPORT_PATH.write_text(json.dumps(payload, indent=2))

            print("Ledger change detected → export updated")

            last = newest

        time.sleep(2)


def build_parser():

    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status")
    s.set_defaults(func=command_status)

    i = sub.add_parser("add-income")
    i.add_argument("--source", required=True)
    i.add_argument("--amount", required=True)
    i.add_argument("--currency", default="USD")
    i.add_argument("--note", default="")
    i.set_defaults(func=command_add_income)

    e = sub.add_parser("add-expense")
    e.add_argument("--category", required=True)
    e.add_argument("--amount", required=True)
    e.add_argument("--currency", default="USD")
    e.add_argument("--note", default="")
    e.set_defaults(func=command_add_expense)

    r = sub.add_parser("snapshot")
    r.add_argument("--label", default="manual")
    r.add_argument("--note", default="")
    r.set_defaults(func=command_snapshot)

    ex = sub.add_parser("export")
    ex.set_defaults(func=command_export)

    w = sub.add_parser("watch")
    w.set_defaults(func=command_watch)

    return parser


def main():

    parser = build_parser()

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
