from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import bcrypt

# 模拟用户数据
users = {
    'admin': {
        'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    }
}

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '请输入用户名和密码'}), 400

    if username not in users:
        return jsonify({'error': '用户名或密码错误'}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), users[username]['password'].encode('utf-8')):
        return jsonify({'error': '用户名或密码错误'}), 401

    # 创建访问令牌
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token, 'message': '登录成功'}), 200

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '请输入用户名和密码'}), 400

    if username in users:
        return jsonify({'error': '用户名已存在'}), 400

    if len(password) < 6:
        return jsonify({'error': '密码长度至少为6位'}), 400

    # 加密密码并添加用户
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users[username] = {'password': hashed_password}

    return jsonify({'message': '注册成功'}), 201

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('newPassword')

    if not username or not new_password:
        return jsonify({'error': '请输入用户名和新密码'}), 400

    if username not in users:
        return jsonify({'error': '用户名不存在'}), 404

    if len(new_password) < 6:
        return jsonify({'error': '新密码长度至少为6位'}), 400

    # 更新密码
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users[username]['password'] = hashed_password

    return jsonify({'message': '密码修改成功'}), 200
