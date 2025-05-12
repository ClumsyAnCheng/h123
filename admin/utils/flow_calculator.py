from collections import defaultdict

def create_pipe_objects(connection_graph, default_params=None):
    """创建管道对象列表"""
    from models.flare_models import Pipe
    
    pipe_list = []
    default_params = default_params or {}  

    for end_node, start_nodes in connection_graph.items():
        for start_node in start_nodes:
            name = f"{start_node}->{end_node}"
            params = default_params.get(name, {})
            
            pipe_obj = Pipe(
                name=name,
                equivalent_length=params.get("equivalent_length"),
                diameter=params.get("diameter"),
                outlet_pressure=params.get("outlet_pressure"),
                roughness=params.get("roughness"),
                cross_area=params.get("cross_area"),
                flow_rate=params.get("flow_rate"),
                avg_temperature=params.get("avg_temperature"),
                avg_molecular_weight=params.get("avg_molecular_weight"),
                mach_number=params.get("mach_number"),
                friction_factor=params.get("friction_factor"),
                inlet_pressure=params.get("inlet_pressure"),
                reynolds_number=params.get("reynolds_number")
            )
            pipe_list.append(pipe_obj)
    
    return pipe_list

def create_discharge_objects(discharge_nodes, default_params=None):
    """创建泄放点对象列表"""
    from models.flare_models import DischargePoint
    
    discharge_objects = []
    default_params = default_params or {}

    for node in discharge_nodes:
        params = default_params.get(node, {})
        discharge_obj = DischargePoint(
            node_id=node,
            flow_rate=params.get("flow_rate"),
            pressure=params.get("pressure"),
            temperature=params.get("temperature"),
            molecular_weight=params.get("molecular_weight"),
            max_backpressure=params.get("max_backpressure"),
            viscosity=params.get("viscosity")
        )
        discharge_objects.append(discharge_obj)

    return discharge_objects

def calculate_pipe_flow_rates(pipe_list, discharge_objects, connection_graph, flare_node):
    """计算各段管道流量"""
    # 构建前向图：终点 -> 起点列表
    forward_graph = defaultdict(list)
    for end_node, start_nodes in connection_graph.items():
        for start_node in start_nodes:
            forward_graph[end_node].append(start_node)

    # 构建泄放点流量映射
    discharge_flow_map = {point.node_id: point.flow_rate for point in discharge_objects}

    # 创建一个映射，名称 -> 管道对象
    name_to_pipe = {pipe.name: pipe for pipe in pipe_list}

    # 定义回溯函数：计算从该节点向前所有泄放点的累计流量
    def backtrack_flow(end_node):
        total_flow = 0
        if end_node in discharge_flow_map:
            return discharge_flow_map[end_node]

        for start_node in forward_graph.get(end_node, []):
            # 管道名
            pipe_name = f"{start_node}->{end_node}"
            sub_flow = backtrack_flow(start_node)
            total_flow += sub_flow
            # 写入管道流量
            if pipe_name in name_to_pipe:
                name_to_pipe[pipe_name].flow_rate = sub_flow
        return total_flow

    # 从火炬装置开始递归计算
    backtrack_flow(flare_node)

    return pipe_list 