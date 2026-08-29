import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class Patient(Base):
    """患者档案"""
    __tablename__ = "patients"
    __table_args__ = (
        Index("ix_patients_name", "name"),
        Index("ix_patients_phone", "phone"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(5), nullable=False, comment="男/女")
    birth_date: Mapped[date | None] = mapped_column(Date)
    age: Mapped[int | None] = mapped_column()
    phone: Mapped[str | None] = mapped_column(String(20))
    id_card: Mapped[str | None] = mapped_column(String(50), comment="身份证号")
    address: Mapped[str | None] = mapped_column(String(200))
    allergies: Mapped[str | None] = mapped_column(Text, comment="过敏史")
    medical_history: Mapped[str | None] = mapped_column(Text, comment="既往病史")
    notes: Mapped[str | None] = mapped_column(Text, comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    consultations: Mapped[list["UlcerConsultation"]] = relationship("UlcerConsultation", back_populates="patient")
