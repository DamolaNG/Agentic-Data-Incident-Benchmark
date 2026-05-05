select
    cast(transaction_id as integer) as transaction_id,
    cast(fraud_label as varchar) as fraud_label,
    cast(label_reason as varchar) as label_reason,
    cast(labeled_at as timestamp) as labeled_at
from {{ source('raw', 'raw_fraud_labels') }}

