"""
Mintellect API Client
Все HTTP-запросы к бэкенду в одном месте.
"""
import requests
from typing import Optional

BASE_URL = "http://localhost:8000/api"


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _r(response: requests.Response):
    """Raise ValueError with readable message, or return parsed JSON."""
    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
            if isinstance(detail, list):
                detail = detail[0].get("msg", str(detail))
            elif isinstance(detail, dict):
                detail = detail.get("message", str(detail))
        except Exception:
            detail = response.text
        raise ValueError(str(detail))
    try:
        return response.json()
    except Exception:
        return {}


# ── AUTH ──────────────────────────────────────────────────────────────────────

def register(nickname: str, login: str, password: str) -> dict:
    r = requests.post(f"{BASE_URL}/register",
                      json={"nickname": nickname, "login": login, "password": password})
    return _r(r)


def login(login_str: str, password: str) -> dict:
    r = requests.post(f"{BASE_URL}/login",
                      json={"login": login_str, "password": password})
    return _r(r)


# ── SCHEDULE ──────────────────────────────────────────────────────────────────

def get_schedule(token: str) -> list:
    return _r(requests.get(f"{BASE_URL}/schedule/my", headers=_headers(token)))


def get_today_schedule(token: str) -> list:
    return _r(requests.get(f"{BASE_URL}/schedule/today", headers=_headers(token)))


def add_lesson(token: str, day_of_week: int, subject: str,
               start_time: str, end_time: str) -> dict:
    return _r(requests.post(f"{BASE_URL}/schedule/", headers=_headers(token),
                            json={"day_of_week": day_of_week, "subject": subject,
                                  "start_time": start_time, "end_time": end_time}))


def bulk_schedule(token: str, lessons: list) -> list:
    return _r(requests.put(f"{BASE_URL}/schedule/bulk",
                           headers=_headers(token), json={"lessons": lessons}))


def delete_lesson(token: str, schedule_id: int) -> dict:
    return _r(requests.delete(f"{BASE_URL}/schedule/{schedule_id}",
                              headers=_headers(token)))


def clear_schedule(token: str) -> bool:
    r = requests.delete(f"{BASE_URL}/schedule/", headers=_headers(token))
    return r.ok


# ── NOTES ─────────────────────────────────────────────────────────────────────

def get_notes(token: str, start_date: str = None,
              end_date: str = None, schedule_id: int = None) -> list:
    params = {}
    if start_date:   params["start_date"] = start_date
    if end_date:     params["end_date"] = end_date
    if schedule_id:  params["schedule_id"] = schedule_id
    return _r(requests.get(f"{BASE_URL}/notes/",
                           headers=_headers(token), params=params))


def get_note(token: str, note_id: int) -> dict:
    return _r(requests.get(f"{BASE_URL}/notes/{note_id}", headers=_headers(token)))


def get_notes_by_date(token: str, date: str) -> list:
    return _r(requests.get(f"{BASE_URL}/notes/by-date/{date}",
                           headers=_headers(token)))


def create_note(token: str, title: str, content: str,
                date: str, schedule_id: Optional[int] = None) -> dict:
    payload = {"title": title, "content": content, "date": date}
    if schedule_id:
        payload["schedule_id"] = schedule_id
    return _r(requests.post(f"{BASE_URL}/notes/",
                            headers=_headers(token), json=payload))


def update_note(token: str, note_id: int, title: str, content: str,
                date: str, schedule_id: Optional[int] = None) -> dict:
    payload = {"title": title, "content": content, "date": date}
    if schedule_id:
        payload["schedule_id"] = schedule_id
    return _r(requests.put(f"{BASE_URL}/notes/{note_id}",
                           headers=_headers(token), json=payload))


def delete_note(token: str, note_id: int) -> bool:
    r = requests.delete(f"{BASE_URL}/notes/{note_id}", headers=_headers(token))
    return r.ok


def get_group_notes(token: str, group_id: int) -> list:
    return _r(requests.get(f"{BASE_URL}/notes/group/{group_id}",
                           headers=_headers(token)))


# ── ATTACHMENTS ───────────────────────────────────────────────────────────────

def upload_attachment(token: str, note_id: int, file_bytes: bytes,
                      filename: str, content_type: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (filename, file_bytes, content_type)}
    return _r(requests.post(f"{BASE_URL}/notes/{note_id}/attachments/",
                            headers=headers, files=files))


def get_attachments(token: str, note_id: int) -> list:
    return _r(requests.get(f"{BASE_URL}/notes/{note_id}/attachments/",
                           headers=_headers(token)))


def download_attachment(token: str, note_id: int, attachment_id: int) -> bytes:
    r = requests.get(f"{BASE_URL}/notes/{note_id}/attachments/{attachment_id}",
                     headers=_headers(token))
    if not r.ok:
        raise ValueError("Не удалось скачать файл")
    return r.content


def delete_attachment(token: str, note_id: int, attachment_id: int) -> bool:
    r = requests.delete(
        f"{BASE_URL}/notes/{note_id}/attachments/{attachment_id}",
        headers=_headers(token))
    return r.ok


# ── GROUPS ────────────────────────────────────────────────────────────────────

def create_group(token: str, name: str, description: str = "") -> dict:
    return _r(requests.post(f"{BASE_URL}/groups/", headers=_headers(token),
                            json={"name": name, "description": description}))


def get_groups(token: str) -> list:
    return _r(requests.get(f"{BASE_URL}/groups/", headers=_headers(token)))


def get_group(token: str, group_id: int) -> dict:
    return _r(requests.get(f"{BASE_URL}/groups/{group_id}",
                           headers=_headers(token)))


def update_group(token: str, group_id: int, name: str, description: str = "") -> dict:
    return _r(requests.put(f"{BASE_URL}/groups/{group_id}",
                           headers=_headers(token),
                           json={"name": name, "description": description}))


def delete_group(token: str, group_id: int) -> bool:
    r = requests.delete(f"{BASE_URL}/groups/{group_id}", headers=_headers(token))
    return r.ok


def add_member(token: str, group_id: int, user_login: str) -> dict:
    return _r(requests.post(f"{BASE_URL}/groups/{group_id}/members",
                            headers=_headers(token),
                            json={"user_login": user_login}))


def remove_member(token: str, group_id: int, user_id: int) -> bool:
    r = requests.delete(f"{BASE_URL}/groups/{group_id}/members/{user_id}",
                        headers=_headers(token))
    return r.ok


def get_members(token: str, group_id: int) -> list:
    return _r(requests.get(f"{BASE_URL}/groups/{group_id}/members",
                           headers=_headers(token)))