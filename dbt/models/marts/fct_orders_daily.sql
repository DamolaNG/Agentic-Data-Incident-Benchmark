select
    cast(order_timestamp as date) as order_date,
    count(*) as order_count,
    sum(order_total) as gross_order_value,
    sum(case when order_status = 'completed' then order_total else 0 end) as completed_order_value
from {{ ref('stg_orders') }}
group by 1

