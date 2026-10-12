from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class CreatedTask(Base):
    __tablename__ = "created_tasks"
    __table_args__ = (
        UniqueConstraint("client_id", "title", "redmine_project_id", name="uq_created_task"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("suggestions.id"), unique=True, nullable=False
    )
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.id"), nullable=False)
    redmine_project_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    redmine_issue_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())