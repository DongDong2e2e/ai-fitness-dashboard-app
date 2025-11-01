from datetime import datetime
from sqlalchemy.orm import Query

def apply_date_range_filter(query: Query, model, date_range_start: str | None, date_range_end: str | None) -> Query:
    if date_range_start and date_range_end:
        start_date = datetime.strptime(date_range_start, "%Y-%m-%d").date()
        end_date = datetime.strptime(date_range_end, "%Y-%m-%d").date()
        query = query.filter(model.date.between(start_date, end_date))
    return query
