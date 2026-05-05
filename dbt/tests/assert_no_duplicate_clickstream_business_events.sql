select
    session_id,
    user_id,
    event_timestamp,
    event_name,
    page_url,
    count(*) as duplicate_count
from {{ ref('stg_events') }}
group by 1, 2, 3, 4, 5
having count(*) > 1

