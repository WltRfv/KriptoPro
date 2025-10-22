import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

print("🔄 Creating ALL database tables...")

app = create_app()

with app.app_context():
    # Создаем все таблицы из наших моделей
    db.create_all()
    print("✅ All tables created!")

    # Проверяем
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📊 All tables: {tables}")

    # Покажем структуру каждой таблицы
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n📋 {table}:")
        for column in columns:
            print(f"   - {column['name']}: {column['type']}")
