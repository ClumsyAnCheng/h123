from flask import Blueprint, request, jsonify
from services.flare_system_service import FlareSystemService
from services.record_service import RecordService

flare_system_bp = Blueprint('flare_system', __name__, url_prefix='/api/v1/flare_system')

@flare_system_bp.route('/check', methods=['POST'])
def check_flare_system():
    """判断装置是否符合规定接口"""
    # 获取JSON请求数据
    data = request.get_json()
    
    if not data:
        return jsonify({
            "status": 400,
            "error_code": "INVALID_JSON",
            "message": "请求数据格式错误，需要JSON格式"
        }), 400
    
    # 调用服务进行校验
    result = FlareSystemService.check_flare_system(data)
    
    # 处理响应状态码
    http_status = 200
    if result.get('status') >= 400:
        http_status = result.get('status')
    
    return jsonify(result), http_status

@flare_system_bp.route('/save', methods=['POST'])
def save_record():
    """保存记录接口"""
    # 获取JSON请求数据
    data = request.get_json()
    
    if not data:
        return jsonify({
            "code": "PARAMETER.INVALID",
            "message": "请求数据格式错误，需要JSON格式",
            "invalid_field": "request"
        }), 400
    
    # 调用服务保存记录
    result, status_code = RecordService.save_record(data)
    
    return jsonify(result), status_code

@flare_system_bp.route('/info', methods=['GET'])
def get_records():
    """获取历史记录接口"""
    # 调用服务获取所有记录
    result, status_code = RecordService.get_records()
    
    return jsonify(result), status_code 