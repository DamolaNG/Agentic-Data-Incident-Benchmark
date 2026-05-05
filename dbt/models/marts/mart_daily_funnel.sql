select
    session_date,
    count(*) as sessions,
    sum(has_product_view) as product_view_sessions,
    sum(has_add_to_cart) as add_to_cart_sessions,
    sum(has_checkout_started) as checkout_started_sessions,
    sum(has_purchase_event) as purchase_sessions,
    round(sum(has_purchase_event) * 1.0 / nullif(count(*), 0), 4) as session_conversion_rate
from {{ ref('int_session_events') }}
group by 1

