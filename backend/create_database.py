import os
import sys
from app import create_app, db

print("🔄 Creating database...")

app = create_app()

with app.app_context():
    # Покажем конфигурацию
    print(f"📁 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Создаем папку instance если нет
    os.makedirs('instance', exist_ok=True)

    # Создаем все таблицы
    db.create_all()
    print("✅ Tables created!")

    # Проверим
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables: {tables}")

    # Проверим файл
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if os.path.exists(db_path):
        print(f"✅ Database file created: {db_path}")
        print(f"📏 File size: {os.path.getsize(db_path)} bytes")
    else:
        print(f"❌ Database file not found at: {db_path}")
