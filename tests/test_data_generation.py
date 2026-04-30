from agentic_data_incident_benchmark.data_generation.generate_orders import build_orders


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

