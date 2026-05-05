select
    s.session_id,
    s.user_id,
    s.session_started_at,
    s.session_date,
    s.device_type,
    s.traffic_source,
    count(e.event_id) as event_count,
    min(e.event_timestamp) as first_event_at,
    max(e.event_timestamp) as last_event_at,
    max(case when e.event_name = 'page_view' then 1 else 0 end) as has_page_view,
    max(case when e.event_name = 'product_view' then 1 else 0 end) as has_product_view,
    max(case when e.event_name = 'add_to_cart' then 1 else 0 end) as has_add_to_cart,
    max(case when e.event_name = 'checkout_started' then 1 else 0 end) as has_checkout_started,
    max(case when e.event_name = 'purchase' then 1 else 0 end) as has_purchase_event
from {{ ref('stg_sessions') }} as s
left join {{ ref('stg_events') }} as e
    on s.session_id = e.session_id
group by 1, 2, 3, 4, 5, 6

