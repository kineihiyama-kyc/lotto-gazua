"""Fetch and persist the latest Lotto 6/45 first-prize history."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.request import ProxyHandler, build_opener


LOTTO_API = (
    "https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?"
    "srchStrLtEpsd=1&srchEndLtEpsd=9999"
)
opener = build_opener(ProxyHandler({}))


def fetch_history():
    with opener.open(LOTTO_API, timeout=20) as response:
        payload = json.load(response)
    rows = payload.get("data", {}).get("list", [])
    history = []
    for row in rows:
        numbers = tuple(sorted(int(row[f"tm{i}WnNo"]) for i in range(1, 7)))
        history.append({"round": int(row["ltEpsd"]), "date": row.get("ltRflYmd", ""), "numbers": numbers})
    if not history:
        raise RuntimeError("No lottery history received")
    return sorted(history, key=lambda item: item["round"])


def update_history(cache_file: Path):
    history = fetch_history()
    temporary_file = cache_file.with_suffix(".json.tmp")
    temporary_file.write_text(json.dumps(history, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary_file.replace(cache_file)
    return history


if __name__ == "__main__":
    cache_file = Path(__file__).with_name("lotto-history.json")
    history = update_history(cache_file)
    latest = history[-1]
    print(f"Updated {len(history)} rounds through {latest['round']} ({latest['date']}).")
