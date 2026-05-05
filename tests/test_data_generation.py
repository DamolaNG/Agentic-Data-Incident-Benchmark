from agentic_data_incident_benchmark.data_generation.generate_orders import build_orders
from agentic_data_incident_benchmark.data_generation.generate_ecommerce_data import build_ecommerce_data


def test_build_orders_returns_expected_columns() -> None:
    orders = build_orders(row_count=3)

    assert list(orders.columns) == [
        "order_id",
        "customer_id",
        "order_timestamp",
        "order_status",
        "order_total",
    ]
    assert len(orders) == 3


def test_build_ecommerce_data_returns_connected_datasets() -> None:
    datasets = build_ecommerce_data()

    assert set(datasets) == {
        "raw_users",
        "raw_sessions",
        "raw_events",
        "raw_transactions",
        "raw_fraud_labels",
    }
    assert datasets["raw_users"]["user_id"].is_unique
    assert datasets["raw_sessions"]["session_id"].is_unique
    assert datasets["raw_events"]["event_id"].is_unique
