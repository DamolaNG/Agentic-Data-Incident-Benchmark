with feature_counts as (
    select
        transaction_id,
        count(*) as feature_rows
    from {{ ref('fct_fraud_features') }}
    group by 1
),

duplicate_features as (
    select transaction_id, feature_rows
    from feature_counts
    where feature_rows > 1
),

missing_features as (
    select
        t.transaction_id,
        0 as feature_rows
    from {{ ref('stg_transactions') }} as t
    left join feature_counts as f
        on t.transaction_id = f.transaction_id
    where f.transaction_id is null
)

select *
from duplicate_features
union all
select *
from missing_features

