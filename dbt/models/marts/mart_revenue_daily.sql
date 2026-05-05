select
    transaction_date as revenue_date,
    count(*) as transaction_count,
    sum(case when transaction_status = 'succeeded' then 1 else 0 end) as succeeded_transactions,
    sum(case when transaction_status = 'succeeded' then amount else 0 end) as gross_revenue,
    avg(case when transaction_status = 'succeeded' then amount else null end) as average_order_value
from {{ ref('stg_transactions') }}
group by 1

