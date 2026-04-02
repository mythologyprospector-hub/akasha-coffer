#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "PyYAML is required. Install it with: pip install pyyaml"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "coffer.yaml"
INCOME_PATH = ROOT / "ledger" / "income.yaml"
EXPENSE_PATH = ROOT / "ledger" / "expenses.yaml"
RESERVE_PATH = ROOT / "ledger" / "reserves.yaml"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def load_config() -> dict[str, Any]:
    return load_yaml(CONFIG_PATH)


def load_income() -> list[dict[str, Any]]:
    return load_yaml(INCOME_PATH).get("income", [])


def load_expenses() -> list[dict[str, Any]]:
    return load_yaml(EXPENSE_PATH).get("expenses", [])


def load_reserves() -> list[dict[str, Any]]:
    return load_yaml(RESERVE_PATH).get("reserves", {}).get("snapshots", [])


def save_income(items: list[dict[str, Any]]) -> None:
    save_yaml(INCOME_PATH, {"income": items})


def save_expenses(items: list[dict[str, Any]]) -> None:
    save_yaml(EXPENSE_PATH, {"expenses": items})


def save_reserves(items: list[dict[str, Any]]) -> None:
    save_yaml(RESERVE_PATH, {"reserves": {"snapshots": items}})


def total_amount(rows: list[dict[str, Any]]) -> float:
    return round(sum(float(row.get("amount", 0)) for row in rows), 2)


def command_status(_: argparse.Namespace) -> None:
    config = load_config()
    income = load_income()
    expenses = load_expenses()
    reserves = load_reserves()

    total_income = total_amount(income)
    total_expenses = total_amount(expenses)
    balance = round(total_income - total_expenses, 2)

    print("==================================")
    print("         AKASHA COFFER")
    print("==================================")
    print(f"Name:    {config.get('coffer', {}).get('name', 'Akasha Coffer')}")
    print(f"Income:  {total_income:.2f}")
    print(f"Expense: {total_expenses:.2f}")
    print(f"Balance: {balance:.2f}")
    print(f"Reserve snapshots: {len(reserves)}")
    print()

    channels = config.get("support_channels", {})
    if channels:
        print("Support Channels:")
        for key, value in channels.items():
            print(f"  - {key}: {value}")
        print()

    buckets = config.get("allocation_buckets", {})
    if buckets:
        print("Allocation Buckets:")
        for name, pct in buckets.items():
            print(f"  - {name}: {pct}%")

def command_add_income(args: argparse.Namespace) -> None:
    income = load_income()
    entry = {
        "timestamp": now_iso(),
        "source": args.source,
        "amount": round(float(args.amount), 2),
        "currency": args.currency,
        "note": args.note,
    }
    income.append(entry)
    save_income(income)
    print("Income entry added:")
    print(json.dumps(entry, indent=2))

def command_add_expense(args: argparse.Namespace) -> None:
    expenses = load_expenses()
    entry = {
        "timestamp": now_iso(),
        "category": args.category,
        "amount": round(float(args.amount), 2),
        "currency": args.currency,
        "note": args.note,
    }
    expenses.append(entry)
    save_expenses(expenses)
    print("Expense entry added:")
    print(json.dumps(entry, indent=2))

def command_snapshot(args: argparse.Namespace) -> None:
    income = total_amount(load_income())
    expenses = total_amount(load_expenses())
    balance = round(income - expenses, 2)

    snapshots = load_reserves()
    entry = {
        "timestamp": now_iso(),
        "label": args.label,
        "balance": balance,
        "note": args.note,
    }
    snapshots.append(entry)
    save_reserves(snapshots)
    print("Reserve snapshot added:")
    print(json.dumps(entry, indent=2))

def command_dump(_: argparse.Namespace) -> None:
    payload = {
        "config": load_config(),
        "income": load_income(),
        "expenses": load_expenses(),
        "reserves": load_reserves(),
    }
    print(json.dumps(payload, indent=2))

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="coffer",
        description="Akasha treasury playground CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Show coffer status")
    status.set_defaults(func=command_status)

    add_income = sub.add_parser("add-income", help="Add an income entry")
    add_income.add_argument("--source", required=True)
    add_income.add_argument("--amount", required=True, type=float)
    add_income.add_argument("--currency", default="USD")
    add_income.add_argument("--note", default="")
    add_income.set_defaults(func=command_add_income)

    add_expense = sub.add_parser("add-expense", help="Add an expense entry")
    add_expense.add_argument("--category", required=True)
    add_expense.add_argument("--amount", required=True, type=float)
    add_expense.add_argument("--currency", default="USD")
    add_expense.add_argument("--note", default="")
    add_expense.set_defaults(func=command_add_expense)

    snapshot = sub.add_parser("snapshot", help="Record a reserve snapshot")
    snapshot.add_argument("--label", default="manual")
    snapshot.add_argument("--note", default="")
    snapshot.set_defaults(func=command_snapshot)

    dump = sub.add_parser("dump", help="Dump full coffer state as JSON")
    dump.set_defaults(func=command_dump)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
