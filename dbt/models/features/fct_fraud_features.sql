select
    t.transaction_id,
    t.user_id,
    t.session_id,
    t.transaction_timestamp,
    t.transaction_date,
    t.amount,
    t.payment_method,
    t.transaction_status,
    u.signup_date,
    u.acquisition_channel,
    u.country,
    us.total_sessions,
    us.device_type_count,
    us.traffic_source_count,
    se.device_type,
    se.traffic_source,
    se.event_count,
    se.has_product_view,
    se.has_add_to_cart,
    se.has_checkout_started,
    se.has_purchase_event,
    fl.fraud_label,
    case when fl.fraud_label = 'fraud' then 1 else 0 end as is_fraud
from {{ ref('stg_transactions') }} as t
left join {{ ref('stg_users') }} as u
    on t.user_id = u.user_id
left join {{ ref('int_user_sessions') }} as us
    on t.user_id = us.user_id
left join {{ ref('int_session_events') }} as se
    on t.session_id = se.session_id
left join {{ ref('stg_fraud_labels') }} as fl
    on t.transaction_id = fl.transaction_id

