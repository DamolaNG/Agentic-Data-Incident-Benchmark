select
    currency,
    count(*) as transaction_count
from {{ ref('stg_transactions') }}
where currency <> 'GBP'
group by 1

