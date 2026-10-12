from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class CalculationRun(Base):
    __tablename__ = "calculation_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False)  # MANUAL / SCHEDULED
    status: Mapped[str] = mapped_column(String(20), nullable=False)        # RUNNING / COMPLETED / FAILED
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)