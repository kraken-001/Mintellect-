from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(UTC))

    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    owned_groups = relationship("Group", back_populates="creator", foreign_keys="Group.created_by")
    group_memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    access_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    expires_at = Column(DateTime, nullable=False)


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_of_week = Column(Integer)  # 0-6 (пн-вс)
    subject = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    user = relationship("User", back_populates="schedules")
    notes = relationship("Note", back_populates="schedule", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    date = Column(Date, nullable=False)

    # Новые поля
    visibility = Column(String, default="private")  # "private" или "group"
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)

    user = relationship("User", back_populates="notes")
    schedule = relationship("Schedule", back_populates="notes")
    group = relationship("Group", back_populates="notes")
    attachments = relationship("Attachment", back_populates="note", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    stored_name = Column(String, nullable=False, unique=True)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)  # в байтах
    uploaded_at = Column(DateTime, default=datetime.now(UTC))

    note = relationship("Note", back_populates="attachments")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    creator = relationship("User", foreign_keys=[created_by], back_populates="owned_groups")
    members = relationship("Membership", back_populates="group", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="group", cascade="all, delete-orphan")


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    role = Column(String, default="member")  # "admin" или "member"
    joined_at = Column(DateTime, default=datetime.now(UTC))

    user = relationship("User", back_populates="group_memberships")
    group = relationship("Group", back_populates="members")