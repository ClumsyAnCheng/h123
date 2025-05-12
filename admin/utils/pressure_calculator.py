import math
from collections import defaultdict

def calculate_pipe_inlet_pressures(pipe_list, connection_graph, flare_node):
    """计算各段管道入口压力"""
    # 构建前向图：终点->起点
    forward_graph = defaultdict(list)
    for end_node, start_nodes in connection_graph.items():
        for start_node in start_nodes:
            forward_graph[end_node].append(start_node)

    # 管道对象映射
    pipe_map = {pipe.name: pipe for pipe in pipe_list}

    # 递归函数：计算起点的所有入口压力
    def backtrack_calculate_pressure(end_node, current_outlet_pressure):
        for start_node in forward_graph.get(end_node, []):
            pipe_name = f"{start_node}->{end_node}"
            pipe = pipe_map.get(pipe_name)
            if pipe is None:
                continue

            pipe.outlet_pressure = current_outlet_pressure  # 使用上一步入口压力作为本段出口压力

            f = pipe.friction_factor
            L = pipe.equivalent_length
            D = pipe.diameter
            M = pipe.mach_number
            P2 = pipe.outlet_pressure

            if None in (f, L, D, M, P2) or P2 <= 0 or M <= 0:
                continue

            left_side = (f * L) / D

            def equation(x):
                if x <= 0 or x >= 1:
                    return float('inf')
                return ((1 - x**2) / (x**2 * M**2)) + math.log(x**2) - left_side

            # 二分法求解 x = P2/P1
            low, high = 1e-6, 1 - 1e-6
            for _ in range(100):
                mid = (low + high) / 2
                val = equation(mid)
                if abs(val) < 1e-6:
                    break
                elif val > 0:
                    low = mid
                else:
                    high = mid
            x = (low + high) / 2
            P1 = P2 / x
            pipe.inlet_pressure = round(P1, 2)

            # 递归处理前一段管道
            backtrack_calculate_pressure(start_node, P1)

    # 从火炬开始，火炬出口压力为已知
    flare_pipe = None
    for pipe in pipe_list:
        if pipe.name.endswith('->' + flare_node):
            flare_pipe = pipe
            break
            
    if flare_pipe is None or flare_pipe.outlet_pressure is None:
        raise ValueError("未设置火炬管道出口压力")

    # 从火炬装置开始回溯计算
    backtrack_calculate_pressure(flare_node, flare_pipe.outlet_pressure)

    return pipe_list

def check_flare_system_qualification(pipe_list, discharge_objects):
    """判断火炬系统是否满足要求"""
    # 泄放点名 -> 安全阀允许背压 映射
    backpressure_map = {point.node_id: point.max_backpressure for point in discharge_objects}

    satisfied = []
    not_satisfied = []

    for pipe in pipe_list:
        start_node, _ = pipe.name.split("->")
        if start_node in backpressure_map:
            safe_backpressure = backpressure_map[start_node]
            actual_inlet_pressure = pipe.inlet_pressure

            if actual_inlet_pressure is None:
                not_satisfied.append((start_node, "未计算入口压力"))
            else:
                # 判断入口压力是否大于安全阀允许背压
                if actual_inlet_pressure <= safe_backpressure:
                    satisfied.append((start_node, actual_inlet_pressure, safe_backpressure))
                else:
                    not_satisfied.append((start_node, actual_inlet_pressure, safe_backpressure))

    # 系统判定结果
    is_qualified = len(not_satisfied) == 0
    
    return is_qualified, satisfied, not_satisfied 