select
    session_date,
    count(*) as session_count,
    sum(case when traffic_source is null then 1 else 0 end) as null_traffic_source_count
from {{ ref('stg_sessions') }}
group by 1
having sum(case when traffic_source is null then 1 else 0 end) * 1.0 / count(*) > 0.05

