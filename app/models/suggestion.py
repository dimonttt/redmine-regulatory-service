from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Suggestion(Base):
    __tablename__ = "suggestions"
    __table_args__ = (
        UniqueConstraint("calculation_run_id", "client_id", "title", name="uq_run_client_title"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    calculation_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("calculation_runs.id"), nullable=False
    )
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # REGULATORY / LLM
    regulatory_work_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("regulatory_works.id")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    estimated_hours: Mapped[float | None] = mapped_column(Numeric(10, 2))
    context: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NEW")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())