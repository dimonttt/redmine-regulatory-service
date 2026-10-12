from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class PlannedHours(Base):
    __tablename__ = "planned_hours"
    __table_args__ = (
        UniqueConstraint("client_id", "period_year", "period_month", name="uq_client_period"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.id"), nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_hours: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    threshold_hours: Mapped[float | None] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())