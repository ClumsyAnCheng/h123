/**
 * 节点工具类
 */
export const nodeUtils = {
  /**
   * 生成唯一ID
   * @returns {string} - 唯一ID
   */
  generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  },

  /**
   * 从连接生成管道ID
   * @param {string} sourceId - 源节点ID 
   * @param {string} targetId - 目标节点ID
   * @returns {string} - 管道ID，格式为 "sourceId->targetId"
   */
  generatePipeId(sourceId, targetId) {
    return `${sourceId}->${targetId}`
  },

  /**
   * 从节点列表和连接列表构建连接图
   * @param {Array} nodes - 节点列表
   * @param {Array} connections - 连接列表
   * @returns {Object} - 连接图
   */
  buildConnectionGraph(nodes, connections) {
    // 找到火炬装置节点
    const flareNode = nodes.find(node => node.type === 'flare_node');
    const flareNodeId = flareNode ? flareNode.id : null;
    
    // 创建连接图
    const graph = {}
    
    // 初始化图，确保节点按照正确的顺序
    nodes.forEach(node => {
      graph[node.id] = []
    })
    
    // 添加连接
    connections.forEach(conn => {
      if (graph[conn.targetId]) {
        graph[conn.targetId].push(conn.sourceId)
      }
    })
    
    return graph
  },

  /**
   * 获取所有泄放点节点
   * @param {Array} nodes - 节点列表 
   * @returns {Array} - 泄放点节点ID列表
   */
  getDischargeNodes(nodes) {
    return nodes
      .filter(node => node.type === 'discharge_node')
      .map(node => node.id)
  },

  /**
   * 获取火炬装置节点
   * @param {Array} nodes - 节点列表
   * @returns {string|null} - 火炬装置节点ID
   */
  getFlareNode(nodes) {
    const flareNode = nodes.find(node => node.type === 'flare_node')
    return flareNode ? flareNode.id : null
  },

  /**
   * 准备API请求数据
   * @param {Array} nodes - 节点列表
   * @param {Array} connections - 连接列表 
   * @param {Array} pipes - 管道列表
   * @returns {Object} - API请求数据
   */
  prepareApiData(nodes, connections, pipes) {
    const graph = this.buildConnectionGraph(nodes, connections)
    const dischargeNodes = this.getDischargeNodes(nodes)
    const flareNode = this.getFlareNode(nodes)
    
    // 提取所有泄放点数据
    const dischargePoints = nodes
      .filter(node => node.type === 'discharge_node')
      .map(node => ({
        node_id: node.id,
        flow_rate: parseFloat(node.data.flow_rate || 0),
        pressure: parseFloat(node.data.pressure || 0),
        temperature: parseFloat(node.data.temperature || 0),
        molecular_weight: parseFloat(node.data.molecular_weight || 0),
        max_backpressure: parseFloat(node.data.max_backpressure || 0),
        viscosity: parseFloat(node.data.viscosity || 0)
      }))
    
    // 简化管道数据，只保留必要字段
    const simplifiedPipes = pipes.map(pipe => ({
      pipe_id: pipe.pipe_id,
      equivalent_length: parseFloat(pipe.equivalent_length || 0),
      diameter: parseFloat(pipe.diameter || 0),
      roughness: parseFloat(pipe.roughness || 0.000045),
      cross_area: parseFloat(pipe.cross_area || 0)
    }))
    
    return {
      system_config: {
        connection_graph: graph,
        discharge_nodes: dischargeNodes,
        flare_node: flareNode
      },
      pipes: simplifiedPipes,
      discharge_points: dischargePoints
    }
  }
}

export default nodeUtils 