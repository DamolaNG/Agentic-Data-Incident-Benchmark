select
    d.metric_date,
    d.session_conversion_rate as dashboard_conversion_rate,
    f.session_conversion_rate as mart_conversion_rate
from {{ ref('dashboard_business_metrics') }} as d
inner join {{ ref('mart_daily_funnel') }} as f
    on d.metric_date = f.session_date
where abs(d.session_conversion_rate - f.session_conversion_rate) > 0.0001

