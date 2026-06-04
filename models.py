from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    entries = relationship(
        "JournalEntry",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    text = Column(Text, nullable=False)
    mood = Column(String(50), nullable=False)

    message = Column(Text)
    insights = Column(Text)
    recommendations = Column(Text)

    user = relationship("User", back_populates="entries")