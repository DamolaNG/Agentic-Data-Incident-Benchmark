select *
from {{ ref('mart_daily_funnel') }}
where product_view_sessions > sessions
   or add_to_cart_sessions > product_view_sessions
   or checkout_started_sessions > add_to_cart_sessions
   or purchase_sessions > checkout_started_sessions

