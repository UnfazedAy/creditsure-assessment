
from datetime import datetime, timezone

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.user import User


def get_dashboard_overview(db: Session) -> dict:
    now = datetime.now(timezone.utc)

    month_start = datetime(
        year=now.year,
        month=now.month,
        day=1,
        tzinfo=timezone.utc
    )

    stmt = select(
        func.count(User.id).label("total_users"),

        func.count(
            case((User.is_active.is_(True), 1))
        ).label("active_users"),

        func.count(
            case((User.is_active.is_(False), 1))
        ).label("inactive_users"),

        func.count(
            case((User.created_at >= month_start, 1))
        ).label("new_users_this_month")
    )

    result = db.execute(stmt).one()

    return {
        "total_users": result.total_users,
        "active_users": result.active_users,
        "inactive_users": result.inactive_users,
        "new_users_this_month": result.new_users_this_month
    }
