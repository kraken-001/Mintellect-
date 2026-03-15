import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import Base, engine
# Импортируем все модели
from app.models import User, Session, Schedule, Note, Attachment, Group, Membership


def init_database():
    print("🐺 Волк АУФ! Инициализация БД...")

    db_path = project_root / "school_notes.db"

    if db_path.exists():
        print(f"⚠️  База данных уже существует: {db_path}")
        response = input("Пересоздать? (данные удалятся) [y/N]: ")
        if response.lower() != 'y':
            print("Отмена.")
            return
        os.remove(db_path)
        print("Старая БД удалена.")

    print("Создаю таблицы...")
    Base.metadata.create_all(bind=engine)

    print("\n✅ Таблицы созданы:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

    print(f"\n📁 Файл БД: {db_path.absolute()}")
    print("\n🔥 Теперь запускай сервер: uvicorn app.main:app --reload")


if __name__ == "__main__":
    init_database()