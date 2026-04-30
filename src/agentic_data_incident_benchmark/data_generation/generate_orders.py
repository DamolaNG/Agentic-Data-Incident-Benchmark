from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import random

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = PROJECT_ROOT / "data" / "generated" / "orders.csv"


def build_orders(row_count: int = 250, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    start = datetime(2026, 1, 1, 9, 0, 0)
    statuses = ["completed", "completed", "completed", "cancelled", "refunded"]

    rows = []
    for order_id in range(1, row_count + 1):
        rows.append(
            {
                "order_id": order_id,
                "customer_id": random.randint(1, 60),
                "order_timestamp": start + timedelta(hours=random.randint(0, 24 * 30)),
                "order_status": random.choice(statuses),
                "order_total": round(random.uniform(10, 500), 2),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    orders = build_orders()
    orders.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(orders)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

