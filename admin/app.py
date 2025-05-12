from flask import Flask, jsonify
from flask_cors import CORS
import pymysql
from config import MYSQL_CONFIG

app = Flask(__name__)
CORS(app)  # 启用CORS支持

def get_db_connection():
    return pymysql.connect(**MYSQL_CONFIG)

# 注册蓝图 - 移到文件末尾避免循环导入
# app.register_blueprint(flare_system_bp)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        "message": "正常运行！"
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status": 404,
        "error_code": "NOT_FOUND",
        "message": "找不到请求的资源"
    }), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "status": 500,
        "error_code": "SERVER_ERROR",
        "message": "服务器内部错误"
    }), 500

# 避免循环导入
from routes.flare_system_routes import flare_system_bp
app.register_blueprint(flare_system_bp)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 