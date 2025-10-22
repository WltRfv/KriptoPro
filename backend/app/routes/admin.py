from flask import Blueprint, request, jsonify

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
def get_users():
    # TODO: Админка для управления пользователями
    return jsonify({"message": "Admin users endpoint"})

@admin_bp.route('/system-status', methods=['GET'])
def system_status():
    # TODO: Статус системы
    return jsonify({"message": "System status endpoint"})