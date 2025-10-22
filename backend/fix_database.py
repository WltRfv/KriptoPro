import os
import sys

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

print("🔄 Setting up database...")

# Создаем приложение вручную
app = Flask(__name__)
app.config.from_object(Config)

# Инициализируем базу данных
db = SQLAlchemy(app)


# Определяем простые модели для теста
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)


class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='BTC')
    address = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=0.0)


# Создаем базу
with app.app_context():
    # Создаем папку instance
    os.makedirs('instance', exist_ok=True)

    # Создаем все таблицы
    db.create_all()
    print("✅ Database tables created!")

    # Проверяем
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables in database: {tables}")

    # Проверяем файл
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ Database file created: {db_path}")
        print(f"📏 File size: {size} bytes")
    else:
        print(f"❌ Database file not found!")
