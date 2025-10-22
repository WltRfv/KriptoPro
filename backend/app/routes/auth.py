from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from .. import db  # Импортируем db из app
from ..models import User, KeyShard  # Импортируем только модели
from ..services.key_service import KeyShardService
from ..services.email_service import EmailService
import uuid
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Базовые поля
    email = data.get('email')
    password = data.get('password')

    # Multi-signature настройки
    is_multi_signature = data.get('is_multi_signature', False)
    team_emails = data.get('team_emails', [])  # Список email команды
    threshold = data.get('threshold', 2)  # Минимум участников

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # Проверяем существует ли пользователь
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    # Создаем пользователя
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        is_active=True
    )
    user.set_password(password)

    # Multi-signature логика
    if is_multi_signature and len(team_emails) >= threshold:
        user.is_multi_signature = True
        user.threshold = threshold
        user.total_members = len(team_emails) + 1  # +1 для владельца

        # Генерируем мастер-ключ
        master_key = KeyShardService.generate_master_key()

        # Разделяем ключ на shards
        shards = KeyShardService.split_secret(master_key, total_shards=len(team_emails), threshold=threshold)

        # Создаем и отправляем shards команде
        for i, team_email in enumerate(team_emails):
            if i < len(shards):
                shard_data = shards[i]

                # Сохраняем shard в базу
                key_shard = KeyShard(
                    user_id=user.id,
                    shard_data=KeyShardService.encrypt_shard(shard_data, master_key),
                    shard_index=shard_data['shard_id'],
                    recipient_email=team_email
                )
                db.session.add(key_shard)

                # Отправляем email
                EmailService.send_key_shard(team_email, shard_data, email)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id,
        "is_multi_signature": user.is_multi_signature
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if user.is_locked():
        return jsonify({"error": "Account temporarily locked"}), 423

    # Для multi-signature пользователей - другой процесс
    if user.is_multi_signature:
        return jsonify({
            "message": "Multi-signature login required",
            "requires_shards": True,
            "threshold": user.threshold,
            "user_id": user.id
        }), 200

    # Обычный логин
    access_token = create_access_token(identity=user.id)
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "is_multi_signature": False
    }), 200


@auth_bp.route('/verify-shards', methods=['POST'])
def verify_shards():
    """Верификация shards для multi-signature входа без JWT-прослойки.

    Ожидает: { "user_id": str, "shards": [...] }
    """
    data = request.get_json() or {}
    provided_shards = data.get('shards', [])
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(user_id)
    if not user or not user.is_multi_signature:
        return jsonify({"error": "Multi-signature not enabled"}), 400

    # TODO: Реализовать настоящую криптографическую верификацию shards
    if len(provided_shards) >= (user.threshold or 0):
        access_token = create_access_token(identity=user.id)
        user.last_login = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "access_token": access_token,
            "message": "Multi-signature verification successful"
        }), 200

    return jsonify({
        "error": f"Not enough shards. Required: {user.threshold}, Provided: {len(provided_shards)}"
    }), 400