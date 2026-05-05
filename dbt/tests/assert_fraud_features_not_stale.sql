with transaction_recency as (
    select max(transaction_date) as max_transaction_date
    from {{ ref('stg_transactions') }}
),

feature_recency as (
    select max(transaction_date) as max_feature_transaction_date
    from {{ ref('fct_fraud_features') }}
)

select
    t.max_transaction_date,
    f.max_feature_transaction_date
from transaction_recency as t
cross join feature_recency as f
where f.max_feature_transaction_date < t.max_transaction_date - interval '1 day'

