import math
from collections import defaultdict

def calculate_pipe_mach_numbers(pipe_list):
    """计算各段管道末端马赫数"""
    for pipe in pipe_list:
        try:
            # 原始参数提取
            flow_rate = pipe.flow_rate          # kg/h
            temperature = pipe.avg_temperature   # K
            mol_weight = pipe.avg_molecular_weight  # g/mol
            cross_area = pipe.cross_area         # cm²

            # 检查有效性
            if None in (flow_rate, temperature, mol_weight, cross_area) or \
               mol_weight == 0 or temperature == 0 or cross_area == 0:
                continue  # 跳过不完整或非法数据

            # 单位换算
            q = flow_rate / 3600                  # kg/s
            A = cross_area / 10000                # m²
            a = ((8314 * temperature) / mol_weight)**0.5  # 声速，m/s
            
            # 计算马赫数
            mach_number = round((q / (A*100000)) * a, 2)  # 保留2位小数

            # 赋值到对象
            pipe.mach_number = mach_number

        except Exception as e:
            print(f"[错误] 计算 {pipe.name} 马赫数失败：{e}")

    return pipe_list

def calculate_pipe_friction_factors(pipe_list, discharge_objects, connection_graph, flare_node):
    """计算各段管道摩擦系数"""
    # 构建前向图
    forward_graph = defaultdict(list)
    for end_node, start_nodes in connection_graph.items():
        for start_node in start_nodes:
            forward_graph[end_node].append(start_node)

    # 提取泄放点数据
    discharge_data = {point.node_id: point for point in discharge_objects}
    name_to_pipe = {pipe.name: pipe for pipe in pipe_list}

    # 回溯函数：收集当前管道可达的泄放点
    def backtrack_discharge_points(end_node):
        if end_node in discharge_data:
            return [discharge_data[end_node]]

        points = []
        for start_node in forward_graph.get(end_node, []):
            points += backtrack_discharge_points(start_node)
        return points

    def calculate_reynolds_number(pipe, related_points):
        Q = pipe.flow_rate  # kg/h
        if not Q or Q == 0:
            return None

        Q_s = Q / 3600  # 转换为 kg/s
        numerator = 0
        denominator = 0
        for point in related_points:
            qi = point.flow_rate / 3600
            Mi = point.molecular_weight
            mu = point.viscosity
            if Mi == 0:
                continue
            weight = qi / Q_s
            numerator += weight * mu * math.sqrt(Mi)
            denominator += weight * math.sqrt(Mi)
        if denominator == 0:
            return None
        
        D = pipe.diameter / 1000  # mm -> m
        viscosity = numerator / denominator
        Re = 4 * Q_s / (math.pi * D * viscosity)
        return Re

    def calculate_friction_factor(Re, roughness, diameter):
        if Re is None or Re <= 0:
            return None
        
        # 初值（Blasius公式估算）
        f = 0.02
        for _ in range(20):
            try:
                left = 1 / math.sqrt(f)
                right = -2.0 * math.log10((roughness / (3.7 * diameter)) + (2.51 / (Re * math.sqrt(f))))
                diff = abs(left - right)
                f = 1 / (right ** 2)
                if diff < 1e-6:
                    break
            except Exception:
                return None
        return round(f, 6)

    # 主流程：逐管道回溯泄放点 -> 计算雷诺数和摩擦系数
    for pipe in pipe_list:
        start_node, end_node = pipe.name.split("->")
        discharge_points = backtrack_discharge_points(start_node)

        Re = calculate_reynolds_number(pipe, discharge_points)
        pipe.reynolds_number = round(Re, 2) if Re else None

        f = calculate_friction_factor(Re, pipe.roughness, pipe.diameter/1000)  # 毫米转米
        pipe.friction_factor = f

    return pipe_list 