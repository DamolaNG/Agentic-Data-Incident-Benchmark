with recent_sessions as (
    select session_id
    from {{ ref('stg_sessions') }}
    where session_date >= (
        select max(session_date) - interval '1 day'
        from {{ ref('stg_sessions') }}
    )
)

select
    rs.session_id,
    coalesce(se.event_count, 0) as event_count
from recent_sessions as rs
left join {{ ref('int_session_events') }} as se
    on rs.session_id = se.session_id
where coalesce(se.event_count, 0) = 0

