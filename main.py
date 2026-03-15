from pydantic import BaseModel
from datetime import datetime, time, date
from typing import Optional, List


# Для регистрации
class UserRegister(BaseModel):
    nickname: str
    login: str
    password: str


# Для авторизации
class UserLogin(BaseModel):
    login: str
    password: str


# Ответ с токеном
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    user_id: int
    nickname: str


# Расписание
class ScheduleBase(BaseModel):
    day_of_week: int  # 0-6 (пн-вс)
    subject: str
    start_time: time
    end_time: time


class ScheduleCreate(ScheduleBase):
    pass


class Schedule(ScheduleBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class ScheduleListCreate(BaseModel):
    lessons: List[ScheduleCreate]


# Заметки
class NoteBase(BaseModel):
    title: str
    content: str
    date: date
    schedule_id: Optional[int] = None


class NoteCreate(NoteBase):
    visibility: str = "private"
    group_id: Optional[int] = None


class NoteUpdate(NoteBase):
    visibility: Optional[str] = None
    group_id: Optional[int] = None


class Note(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    visibility: str
    group_id: Optional[int] = None

    class Config:
        orm_mode = True


# Для главной страницы - текущие уроки
class TodayLesson(BaseModel):
    subject: str
    time: str
    status: str  # "current", "next", "previous", "future"


# Схемы для вложений
class AttachmentBase(BaseModel):
    file_name: str
    mime_type: str
    size: int


class AttachmentCreate(AttachmentBase):
    pass


class Attachment(AttachmentBase):
    id: int
    note_id: int
    stored_name: str
    uploaded_at: datetime

    class Config:
        orm_mode = True


# Схемы для групп
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class Group(GroupBase):
    id: int
    created_by: int
    created_at: datetime
    members_count: Optional[int] = 0

    class Config:
        orm_mode = True


# Членство в группе
class MembershipBase(BaseModel):
    user_id: int
    group_id: int
    role: str


class MembershipCreate(BaseModel):
    user_login: str  # добавляем по логину


class Membership(MembershipBase):
    id: int
    joined_at: datetime

    class Config:
        orm_mode = True


# Заметка с вложениями
class NoteWithAttachments(Note):
    attachments: List[Attachment] = []

    class Config:
        orm_mode = True