<template>
  <div class="node-component">
    <div class="component-list">
      <h3>组件列表</h3>
      <div class="component-items">
        <!-- 泄放点组件 -->
        <div 
          class="component-item discharge-node" 
          draggable="true" 
          @dragstart="onDragStart($event, 'discharge_node')"
        >
          <el-icon><CircleClose /></el-icon>
          <span>泄放点</span>
        </div>
        
        <!-- 火炬装置组件 -->
        <div 
          class="component-item flare-node" 
          draggable="true" 
          @dragstart="onDragStart($event, 'flare_node')"
        >
          <el-icon><Aim /></el-icon>
          <span>火炬装置</span>
        </div>
        
        <!-- 普通节点组件 -->
        <div 
          class="component-item normal-node" 
          draggable="true" 
          @dragstart="onDragStart($event, 'normal_node')"
        >
          <el-icon><Position /></el-icon>
          <span>普通节点</span>
        </div>
        
        <!-- 三通节点组件 -->
        <div 
          class="component-item t-node" 
          draggable="true" 
          @dragstart="onDragStart($event, 't_node')"
        >
          <el-icon><Connection /></el-icon>
          <span>三通节点</span>
        </div>
        
        <!-- 管道组件 -->
        <div 
          class="component-item pipe" 
          draggable="true" 
          @dragstart="onDragStart($event, 'pipe')"
        >
          <el-icon><Minus /></el-icon>
          <span>管道</span>
        </div>
        
        <!-- 分隔线 -->
        <div class="component-divider">
          <small>页面展示组件（不参与计算）</small>
        </div>
        
        <!-- 分离器组件 -->
        <div 
          class="component-item separator" 
          draggable="true" 
          @dragstart="onDragStart($event, 'separator')"
        >
          <el-icon><SetUp /></el-icon>
          <span>分离器</span>
        </div>
        
        <!-- 变径连接组件 -->
        <div 
          class="component-item reducer" 
          draggable="true" 
          @dragstart="onDragStart($event, 'reducer')"
        >
          <el-icon><Share /></el-icon>
          <span>变径连接</span>
        </div>
        
        <!-- 弯头组件 -->
        <div 
          class="component-item elbow" 
          draggable="true" 
          @dragstart="onDragStart($event, 'elbow')"
        >
          <el-icon><Refresh /></el-icon>
          <span>弯头</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { nodeUtils } from '../utils/node-utils'

export default {
  name: 'NodeComponents',
  props: {
    nodes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['add-node'],
  methods: {
    onDragStart(event, type) {
      console.log('开始拖拽组件类型:', type);
      
      // 获取下一个可用的简单字母ID
      const nodeId = this.getNextSimpleId(type);
      console.log('生成的节点ID:', nodeId);
      
      // 设置拖拽数据
      const nodeData = {
        id: nodeId,
        type,
        position: { x: 0, y: 0 },
        data: this.getDefaultData(type, nodeId)
      }
      
      try {
        // 序列化数据
        const jsonData = JSON.stringify(nodeData);
        
        // 设置MIME类型和数据 - 注意：Firefox需要先设置text/plain
        event.dataTransfer.setData('text/plain', jsonData);
        
        // 部分浏览器支持多种类型
        try {
          event.dataTransfer.setData('application/json', jsonData);
        } catch (e) {
          console.log('不支持设置application/json格式');
        }
        
        event.dataTransfer.effectAllowed = 'copy';
        
        console.log('拖拽开始，数据已设置:', nodeData);
        
        // 设置拖拽图像
        const dragImage = document.createElement('div');
        dragImage.style.width = '40px';
        dragImage.style.height = '40px';
        dragImage.style.borderRadius = '50%';
        dragImage.style.backgroundColor = '#fff';
        dragImage.style.border = '1px solid #ddd';
        dragImage.style.position = 'absolute';
        dragImage.style.top = '-1000px';
        document.body.appendChild(dragImage);
        
        event.dataTransfer.setDragImage(dragImage, 20, 20);
        
        // 延迟移除拖拽图像元素
        setTimeout(() => {
          document.body.removeChild(dragImage);
        }, 0);
      } catch (e) {
        console.error('拖拽数据设置失败:', e);
      }
    },
    
    // 获取下一个简单ID（字母）
    getNextSimpleId(type) {
      // 预定义的ID映射
      const typeIdMapping = {
        'flare_node': ['e'],
        'discharge_node': ['a', 'b', 'c', 'd'],
        'normal_node': ['h', 'g'],
        't_node': ['f', 'i']
      };
      
      // 对于展示组件，使用自动三字符编号
      if (['separator', 'reducer', 'elbow'].includes(type)) {
        const prefix = type.charAt(0).toUpperCase();
        const count = this.nodes.filter(node => node.type === type).length;
        return `${prefix}${(count + 1).toString().padStart(2, '0')}`;
      }
      
      // 获取该类型的预定义ID列表
      const availableIds = typeIdMapping[type] || [type.charAt(0)];
      
      // 获取该类型已使用的ID
      const usedIds = this.nodes
        .filter(node => node.type === type)
        .map(node => node.id);
      
      console.log('当前已使用的ID:', usedIds, '可用ID:', availableIds);
      
      // 找到第一个未使用的ID
      for (const id of availableIds) {
        if (!usedIds.includes(id)) {
          return id;
        }
      }
      
      // 如果所有预定义ID都被使用了，返回其中一个
      return availableIds[0];
    },
    
    getDefaultData(type, nodeId) {
      switch (type) {
        case 'discharge_node':
          return {
            node_id: nodeId,
            flow_rate: 0,
            pressure: 0,
            temperature: 0,
            molecular_weight: 0,
            max_backpressure: 0,
            viscosity: 0
          }
        case 'pipe':
          return {
            pipe_id: '',
            equivalent_length: 0,
            diameter: 0,
            roughness: 0.000045,
            cross_area: 0
          }
        case 'separator':
          return {
            name: nodeId,
            resistance_coefficient: 2.5, // 默认阻力系数
            target_pipe: null // 将要连接到的管道ID
          }
        case 'reducer':
          return {
            name: nodeId,
            inlet_diameter: 0, // 入口内径
            outlet_diameter: 0, // 出口内径
            length: 0, // 长度
            roughness: 0.000045, // 绝对粗糙度
            target_pipe: null // 将要连接到的管道ID
          }
        case 'elbow':
          return {
            name: nodeId,
            resistance_coefficient: 1.5, // 弯头阻力系数
            target_pipe: null // 将要连接到的管道ID
          }
        default:
          return {}
      }
    }
  }
}
</script>

<style scoped>
.node-component {
  width: 100%;
  height: 100%;
  padding: 10px;
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.component-list {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 10px;
  background-color: #f9f9f9;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.component-list h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #333;
  text-align: center;
}

.component-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
}

.component-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: move;
  transition: all 0.2s ease;
  user-select: none;
}

.component-item:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.component-item i {
  margin-right: 10px;
  font-size: 18px;
}

.component-divider {
  margin: 8px 0;
  text-align: center;
  color: #909399;
  font-size: 12px;
  border-top: 1px dashed #dcdfe6;
  padding-top: 5px;
}

.discharge-node {
  color: #f56c6c;
}

.flare-node {
  color: #e6a23c;
}

.normal-node {
  color: #409eff;
}

.t-node {
  color: #67c23a;
}

.pipe {
  color: #909399;
}

.separator {
  color: #8e44ad;
}

.reducer {
  color: #2c3e50;
}

.elbow {
  color: #16a085;
}
</style> 