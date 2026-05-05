from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import random

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "generated"

COUNTRIES = ["GB", "US", "IE", "DE", "FR"]
ACQUISITION_CHANNELS = ["organic", "paid_search", "paid_social", "email", "referral"]
DEVICES = ["desktop", "mobile", "tablet"]
TRAFFIC_SOURCES = ["google", "facebook", "newsletter", "direct", "partner"]
EVENT_FLOW = ["page_view", "product_view", "add_to_cart", "checkout_started", "purchase"]
PAYMENT_METHODS = ["card", "paypal", "apple_pay", "google_pay"]
TRANSACTION_STATUSES = ["succeeded", "failed", "refunded"]


def _choice_weighted(values: list[str], weights: list[float]) -> str:
    return random.choices(values, weights=weights, k=1)[0]


def build_ecommerce_data(seed: int = 42) -> dict[str, pd.DataFrame]:
    random.seed(seed)
    base_date = datetime(2026, 1, 1, 8, 0, 0)

    users = []
    for user_id in range(1, 301):
        signup_date = base_date.date() + timedelta(days=random.randint(0, 30))
        users.append(
            {
                "user_id": user_id,
                "signup_date": signup_date.isoformat(),
                "acquisition_channel": random.choice(ACQUISITION_CHANNELS),
                "country": random.choice(COUNTRIES),
                "is_active": random.choice([True, True, True, False]),
            }
        )

    sessions = []
    events = []
    transactions = []
    fraud_labels = []
    event_id = 1
    transaction_id = 1

    for session_id in range(1, 801):
        user = random.choice(users)
        session_started_at = base_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        device_type = random.choice(DEVICES)
        traffic_source = random.choice(TRAFFIC_SOURCES)

        sessions.append(
            {
                "session_id": session_id,
                "user_id": user["user_id"],
                "session_started_at": session_started_at.isoformat(sep=" "),
                "device_type": device_type,
                "traffic_source": traffic_source,
            }
        )

        reached_product = random.random() < 0.72
        reached_cart = reached_product and random.random() < 0.48
        reached_checkout = reached_cart and random.random() < 0.62
        reached_purchase = reached_checkout and random.random() < 0.58
        flow = ["page_view"]
        if reached_product:
            flow.append("product_view")
        if reached_cart:
            flow.append("add_to_cart")
        if reached_checkout:
            flow.append("checkout_started")
        if reached_purchase:
            flow.append("purchase")

        for offset, event_name in enumerate(flow):
            events.append(
                {
                    "event_id": event_id,
                    "session_id": session_id,
                    "user_id": user["user_id"],
                    "event_timestamp": (
                        session_started_at + timedelta(minutes=offset * random.randint(1, 6))
                    ).isoformat(sep=" "),
                    "event_name": event_name,
                    "page_url": f"/{event_name.replace('_', '-')}",
                }
            )
            event_id += 1

        if reached_purchase:
            amount = round(random.uniform(15, 350), 2)
            status = _choice_weighted(TRANSACTION_STATUSES, [0.9, 0.06, 0.04])
            transaction_timestamp = session_started_at + timedelta(minutes=random.randint(4, 30))

            transactions.append(
                {
                    "transaction_id": transaction_id,
                    "session_id": session_id,
                    "user_id": user["user_id"],
                    "transaction_timestamp": transaction_timestamp.isoformat(sep=" "),
                    "amount": amount,
                    "currency": "GBP",
                    "payment_method": random.choice(PAYMENT_METHODS),
                    "transaction_status": status,
                }
            )

            fraud_probability = 0.03
            if amount > 275:
                fraud_probability += 0.08
            if device_type == "mobile" and traffic_source in {"facebook", "partner"}:
                fraud_probability += 0.03
            fraud_label = "fraud" if random.random() < fraud_probability else "legitimate"

            fraud_labels.append(
                {
                    "transaction_id": transaction_id,
                    "fraud_label": fraud_label,
                    "label_reason": "risk_rule" if fraud_label == "fraud" else "cleared",
                    "labeled_at": (transaction_timestamp + timedelta(days=1)).isoformat(sep=" "),
                }
            )
            transaction_id += 1

    return {
        "raw_users": pd.DataFrame(users),
        "raw_sessions": pd.DataFrame(sessions),
        "raw_events": pd.DataFrame(events),
        "raw_transactions": pd.DataFrame(transactions),
        "raw_fraud_labels": pd.DataFrame(fraud_labels),
    }


def write_ecommerce_data() -> dict[str, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    datasets = build_ecommerce_data()
    written_paths = {}

    for name, frame in datasets.items():
        path = OUTPUT_DIR / f"{name}.csv"
        frame.to_csv(path, index=False)
        written_paths[name] = path

    return written_paths


def main() -> None:
    written_paths = write_ecommerce_data()
    for name, path in written_paths.items():
        print(f"Wrote {name} to {path}")


if __name__ == "__main__":
    main()
