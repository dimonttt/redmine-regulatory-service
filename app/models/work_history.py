from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class WorkHistory(Base):
    __tablename__ = "work_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.id"), nullable=False)
    regulatory_work_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("regulatory_works.id")
    )
    redmine_issue_id: Mapped[int | None] = mapped_column(BigInteger)
    redmine_time_entry_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    subject: Mapped[str | None] = mapped_column(String(500))
    hours: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    spent_on: Mapped[date] = mapped_column(Date, nullable=False)
    activity: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())