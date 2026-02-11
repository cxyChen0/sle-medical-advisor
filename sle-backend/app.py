from flask import Flask
from flask_cors import CORS
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入蓝图
from app.api.auth import bp as auth_bp
from app.api.patient import bp as patient_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'

# 启用CORS
CORS(app)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
