import time
import datetime
from utils.flow_calculator import create_pipe_objects, create_discharge_objects, calculate_pipe_flow_rates
from utils.temperature_molecular_calculator import calculate_pipe_avg_temperatures, calculate_pipe_avg_molecular_weight
from utils.mach_number_calculator import calculate_pipe_mach_numbers, calculate_pipe_friction_factors
from utils.pressure_calculator import calculate_pipe_inlet_pressures, check_flare_system_qualification
from utils.data_mapper import map_request_to_pipe_params, map_request_to_discharge_params

class FlareSystemService:
    @staticmethod
    def check_flare_system(data):
        start_time = time.time()
        
        try:
            # 1. 提取系统配置
            system_config = data.get('system_config', {})
            connection_graph = system_config.get('connection_graph', {})
            discharge_nodes = system_config.get('discharge_nodes', [])
            flare_node = system_config.get('flare_node')
            
            # 检查必要参数
            if not connection_graph or not discharge_nodes or not flare_node:
                return {
                    "status": 400,
                    "error_code": "INVALID_INPUT",
                    "message": "系统配置缺少必要参数"
                }
            
            # 2. 提取管道参数
            pipes_data = data.get('pipes', [])
            discharge_points_data = data.get('discharge_points', [])
            
            # 3. 映射到内部数据结构
            pipe_params = map_request_to_pipe_params(pipes_data)
            discharge_params = map_request_to_discharge_params(discharge_points_data)
            
            # 4. 创建管道和泄放点对象
            pipe_objects = create_pipe_objects(connection_graph, pipe_params)
            discharge_objects = create_discharge_objects(discharge_nodes, discharge_params)
            
            # 5. 执行计算流程
            pipe_objects = calculate_pipe_flow_rates(pipe_objects, discharge_objects, connection_graph, flare_node)
            pipe_objects = calculate_pipe_avg_temperatures(pipe_objects, discharge_objects, connection_graph)
            pipe_objects = calculate_pipe_avg_molecular_weight(pipe_objects, discharge_objects, connection_graph)
            pipe_objects = calculate_pipe_mach_numbers(pipe_objects)
            pipe_objects = calculate_pipe_friction_factors(pipe_objects, discharge_objects, connection_graph, flare_node)
            pipe_objects = calculate_pipe_inlet_pressures(pipe_objects, connection_graph, flare_node)
            
            # 6. 进行校验判断
            is_qualified, satisfied, not_satisfied = check_flare_system_qualification(pipe_objects, discharge_objects)
            
            # 7. 构建返回结果
            end_time = time.time()
            calculation_cost = round(end_time - start_time, 3)
            
            # 成功返回
            return {
                "status": 200,
                "message": "安全检查完成",
                "result": {
                    "qualified": is_qualified,
                    "check_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "discharge_point_count": len(discharge_nodes)
                },
                "diagnostics": {
                    "api_version": "天哥基础版",
                    "calculation_cost": calculation_cost
                }
            }
            
        except Exception as e:
            # 异常情况返回
            return {
                "status": 503,
                "error_code": "PRESSURE_CALCULATION_FAILED",
                "message": f"压力计算引擎异常: {str(e)}",
                "retry_after": 5
            } 