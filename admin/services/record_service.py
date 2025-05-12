import datetime
import pymysql
from config import MYSQL_CONFIG
import iso8601

class RecordService:
    @staticmethod
    def get_db_connection():
        """获取数据库连接"""
        return pymysql.connect(**MYSQL_CONFIG)
        
    @staticmethod
    def save_record(data):
        """保存记录到数据库"""
        try:
            # 验证记录时间格式
            record_time = data.get('record_time')
            if not record_time:
                return {
                    "code": "PARAMETER.INVALID",
                    "message": "记录时间不能为空",
                    "invalid_field": "record_time"
                }, 400
            
            try:
                # 验证ISO8601格式
                parsed_time = iso8601.parse_date(record_time)
            except ValueError:
                return {
                    "code": "PARAMETER.INVALID",
                    "message": "记录时间格式错误，需符合ISO8601标准",
                    "invalid_field": "record_time"
                }, 400
            
            # 验证本地路径
            local_path = data.get('local_path')
            if not local_path:
                return {
                    "code": "PARAMETER.INVALID",
                    "message": "本地路径不能为空",
                    "invalid_field": "local_path"
                }, 400
            
            # 备注可以为空
            remark = data.get('remark', '')
            
            # 插入数据
            conn = RecordService.get_db_connection()
            try:
                with conn.cursor() as cursor:
                    sql = """
                    INSERT INTO sys_record 
                    (record_time, local_path, remark) 
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql, (parsed_time, local_path, remark))
                    record_id = cursor.lastrowid
                conn.commit()
                
                # 返回成功结果
                return {
                    "code": "SUCCESS",
                    "message": "记录保存成功",
                    "data": {
                        "record_id": record_id,
                        "created_at": datetime.datetime.now().isoformat() + 'Z'
                    }
                }, 200
            finally:
                conn.close()
                
        except pymysql.MySQLError as e:
            # 数据库错误
            return {
                "code": "DATABASE_ERROR",
                "message": f"数据库操作失败: {str(e)}"
            }, 500
        except Exception as e:
            # 其他错误
            return {
                "code": "INTERNAL_ERROR",
                "message": f"服务器内部错误: {str(e)}"
            }, 500
    
    @staticmethod
    def get_records():
        """获取所有历史记录"""
        try:
            conn = RecordService.get_db_connection()
            try:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    sql = """
                    SELECT id, record_time, local_path, remark
                    FROM sys_record
                    ORDER BY record_time DESC
                    """
                    cursor.execute(sql)
                    records = cursor.fetchall()
                    
                    # 处理日期格式转为ISO8601
                    for record in records:
                        if isinstance(record['record_time'], datetime.datetime):
                            record['record_time'] = record['record_time'].isoformat() + 'Z'
                
                # 返回记录列表
                return {
                    "data": records
                }, 200
            finally:
                conn.close()
                
        except pymysql.MySQLError as e:
            # 数据库错误
            return {
                "error": "DATABASE_ERROR",
                "message": f"数据库查询失败: {str(e)}"
            }, 500
        except Exception as e:
            # 其他错误
            return {
                "error": "INTERNAL_ERROR",
                "message": f"服务器内部错误: {str(e)}"
            }, 500 