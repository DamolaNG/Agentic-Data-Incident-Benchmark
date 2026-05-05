select fl.*
from {{ ref('stg_fraud_labels') }} as fl
left join {{ ref('stg_transactions') }} as t
    on fl.transaction_id = t.transaction_id
where t.transaction_id is null

