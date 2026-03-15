import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_MIME_TYPES = [
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def save_upload_file(upload_file: UploadFile, user_id: int, note_id: int) -> dict:
    # Проверка MIME-типа
    if upload_file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"Неподдерживаемый тип файла: {upload_file.content_type}")

    # Чтение и проверка размера
    file_content = await upload_file.read()
    file_size = len(file_content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(400, f"Файл слишком большой (макс. {MAX_FILE_SIZE // 1024 // 1024} MB)")

    # Генерация уникального имени
    ext = os.path.splitext(upload_file.filename)[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"

    # Создание папки пользователя и заметки
    user_dir = UPLOAD_DIR / f"user_{user_id}"
    user_dir.mkdir(exist_ok=True)
    note_dir = user_dir / f"note_{note_id}"
    note_dir.mkdir(exist_ok=True)

    file_path = note_dir / stored_name
    with open(file_path, "wb") as f:
        f.write(file_content)

    return {
        "file_name": upload_file.filename,
        "stored_name": stored_name,
        "mime_type": upload_file.content_type,
        "size": file_size,
    }


def delete_attachment_file(stored_name: str) -> bool:
    for root, dirs, files in os.walk(UPLOAD_DIR):
        if stored_name in files:
            os.remove(os.path.join(root, stored_name))
            return True
    return False