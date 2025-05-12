def map_request_to_pipe_params(pipes_data):
    """将请求中的管道数据映射到内部管道参数格式"""
    pipe_params = {}
    
    for pipe in pipes_data:
        pipe_id = pipe.get("pipe_id")
        pipe_params[pipe_id] = {
            "equivalent_length": pipe.get("equivalent_length"),
            "diameter": pipe.get("diameter"),
            "roughness": pipe.get("roughness"),
            "cross_area": pipe.get("cross_area"),
            "outlet_pressure": None,  # 需要计算
            "flow_rate": None,        # 需要计算
            "avg_temperature": None,  # 需要计算
            "avg_molecular_weight": None,  # 需要计算
            "mach_number": None,      # 需要计算
            "friction_factor": None,  # 需要计算
            "inlet_pressure": None,   # 需要计算
            "reynolds_number": None   # 需要计算
        }
    
    # 设置火炬装置出口压力
    flare_pipe_id = None
    for pipe_id in pipe_params:
        if pipe_id.endswith("->e"):  # 假设e为火炬节点，可根据实际情况调整
            flare_pipe_id = pipe_id
            break
    
    if flare_pipe_id:
        pipe_params[flare_pipe_id]["outlet_pressure"] = 100000  # 100kPa，固定值
        
    return pipe_params

def map_request_to_discharge_params(discharge_points_data):
    """将请求中的泄放点数据映射到内部泄放点参数格式"""
    discharge_params = {}
    
    for point in discharge_points_data:
        node_id = point.get("node_id")
        discharge_params[node_id] = {
            "flow_rate": point.get("flow_rate"),
            "pressure": point.get("pressure"),
            "temperature": point.get("temperature"),
            "molecular_weight": point.get("molecular_weight"),
            "max_backpressure": point.get("max_backpressure"),
            "viscosity": point.get("viscosity")
        }
        
    return discharge_params 