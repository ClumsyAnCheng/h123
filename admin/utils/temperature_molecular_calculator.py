from collections import defaultdict

def calculate_pipe_avg_temperatures(pipe_list, discharge_objects, connection_graph):
    """计算各段管道平均温度"""
    # 构建前向图
    forward_graph = defaultdict(list)
    for end_node, start_nodes in connection_graph.items():
        for start_node in start_nodes:
            forward_graph[end_node].append(start_node)

    # 构建泄放点数据表
    discharge_data = {point.node_id: (point.temperature, point.flow_rate) 
                      for point in discharge_objects}

    # 管道映射
    name_to_pipe = {pipe.name: pipe for pipe in pipe_list}

    # 递归计算温度
    def backtrack_temperature(end_node):
        if end_node in discharge_data:
            temp, flow = discharge_data[end_node]
            return temp * flow, flow

        total_temp_product = 0
        total_flow = 0
        for start_node in forward_graph.get(end_node, []):
            pipe_name = f"{start_node}->{end_node}"
            sub_temp_product, sub_flow = backtrack_temperature(start_node)
            total_temp_product += sub_temp_product
            total_flow += sub_flow
            
            # 更新该管道的平均温度（保留整数）
            if pipe_name in name_to_pipe and sub_flow > 0:
                name_to_pipe[pipe_name].avg_temperature = round(sub_temp_product / sub_flow)
        return total_temp_product, total_flow

    # 从火炬装置开始递归
    end_node = list(forward_graph.keys())[0]  # 假设第一个就是火炬节点
    backtrack_temperature(end_node)

    return pipe_list

def calculate_pipe_avg_molecular_weight(pipe_list, discharge_objects, connection_graph):
    """计算各段管道平均分子量"""
    # 构建前向图
    forward_graph = defaultdict(list)
    for end_node, start_nodes in connection_graph.items():
        for start_node in start_nodes:
            forward_graph[end_node].append(start_node)

    # 泄放点数据：名称 -> (分子量, 泄放量)
    discharge_data = {point.node_id: (point.molecular_weight, point.flow_rate) 
                      for point in discharge_objects}

    # 管道映射
    name_to_pipe = {pipe.name: pipe for pipe in pipe_list}

    # 递归：返回 (总泄放量 Σq, Σ(q/M))
    def backtrack(end_node):
        total_q = 0
        total_q_div_M = 0

        for start_node in forward_graph.get(end_node, []):
            pipe_name = f"{start_node}->{end_node}"

            # 若起点是泄放点，直接获取数据并赋值
            if start_node in discharge_data:
                M, q = discharge_data[start_node]
                if M == 0:
                    raise ValueError(f"泄放点 {start_node} 分子量不能为0")
                if pipe_name in name_to_pipe:
                    name_to_pipe[pipe_name].avg_molecular_weight = round(q / (q / M))
                total_q += q
                total_q_div_M += q / M
            else:
                # 起点继续向上回溯
                sub_q, sub_q_div_M = backtrack(start_node)
                total_q += sub_q
                total_q_div_M += sub_q_div_M
                if pipe_name in name_to_pipe and sub_q_div_M > 0:
                    name_to_pipe[pipe_name].avg_molecular_weight = round(sub_q / sub_q_div_M)

        return total_q, total_q_div_M

    # 从火炬装置开始递归
    end_node = list(forward_graph.keys())[0]  # 假设第一个就是火炬节点
    backtrack(end_node)
    
    return pipe_list 