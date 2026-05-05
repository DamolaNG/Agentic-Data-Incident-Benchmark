select
    coalesce(f.session_date, r.revenue_date) as metric_date,
    coalesce(f.sessions, 0) as sessions,
    coalesce(f.product_view_sessions, 0) as product_view_sessions,
    coalesce(f.add_to_cart_sessions, 0) as add_to_cart_sessions,
    coalesce(f.checkout_started_sessions, 0) as checkout_started_sessions,
    coalesce(f.purchase_sessions, 0) as purchase_sessions,
    coalesce(f.session_conversion_rate, 0) as session_conversion_rate,
    coalesce(r.transaction_count, 0) as transaction_count,
    coalesce(r.succeeded_transactions, 0) as succeeded_transactions,
    coalesce(r.gross_revenue, 0) as gross_revenue,
    coalesce(r.average_order_value, 0) as average_order_value
from {{ ref('mart_daily_funnel') }} as f
full outer join {{ ref('mart_revenue_daily') }} as r
    on f.session_date = r.revenue_date

