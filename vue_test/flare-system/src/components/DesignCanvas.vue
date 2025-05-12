<template>
  <div class="design-canvas">
    <div 
      class="canvas"
      ref="canvasRef"
      @dragover="onDragOver"
      @drop="onDrop"
      @click="onCanvasClick"
    >
      <!-- 渲染所有节点 -->
      <div 
        v-for="node in nodes" 
        :key="node.id"
        class="node"
        :class="[node.type, { selected: selectedNode === node.id }]"
        :style="{ left: `${node.position.x}px`, top: `${node.position.y}px` }"
        @click.stop="selectNode(node)"
        @mousedown="startDragging($event, node)"
        v-show="!isSpecialComponent(node.type)"
      >
        <div class="node-icon">
          <el-icon v-if="node.type === 'discharge_node'"><CircleClose /></el-icon>
          <el-icon v-else-if="node.type === 'flare_node'"><Aim /></el-icon>
          <el-icon v-else-if="node.type === 'normal_node'"><Position /></el-icon>
          <el-icon v-else-if="node.type === 't_node'"><Connection /></el-icon>
        </div>
        <div class="node-label">{{ getNodeLabel(node) }}</div>
      </div>
      
      <!-- 渲染所有连接 -->
      <svg class="connections">
        <g
          v-for="connection in connections"
          :key="connection.id"
          @click.stop="selectConnection(connection)"
          class="connection-group"
          :class="{ selected: selectedConnection === connection.id }"
        >
          <!-- 管道连接线 -->
          <line
            :x1="getNodePosition(connection.sourceId).x"
            :y1="getNodePosition(connection.sourceId).y"
            :x2="getNodePosition(connection.targetId).x"
            :y2="getNodePosition(connection.targetId).y"
            stroke="#666"
            stroke-width="2"
          />
          
          <!-- 管道标签 -->
          <text
            :x="getConnectionLabelPosition(connection).x"
            :y="getConnectionLabelPosition(connection).y"
            text-anchor="middle"
            dominant-baseline="middle"
            fill="#333"
            font-size="10"
            class="pipe-label"
          >
            {{ getPipeLabel(connection) }}
          </text>
          
          <!-- 点击区域（更宽以便更容易点击） -->
          <line
            :x1="getNodePosition(connection.sourceId).x"
            :y1="getNodePosition(connection.sourceId).y"
            :x2="getNodePosition(connection.targetId).x"
            :y2="getNodePosition(connection.targetId).y"
            stroke="transparent"
            stroke-width="10"
            class="connection-hitbox"
          />
        </g>
      </svg>
      
      <!-- 渲染分离器组件 -->
      <div
        v-for="node in getSpecialComponents('separator')"
        :key="node.id"
        class="separator-component"
        :class="{ selected: selectedNode === node.id }"
        :style="getSeparatorPosition(node)"
        @click.stop="selectNode(node)"
        @mousedown="startDragging($event, node)"
      >
        <div class="component-icon">
          <el-icon><SetUp /></el-icon>
        </div>
        <div class="component-label">{{ node.data.name }}</div>
      </div>
      
      <!-- 渲染变径连接组件 -->
      <div
        v-for="node in getSpecialComponents('reducer')"
        :key="node.id"
        class="reducer-component"
        :class="{ selected: selectedNode === node.id }"
        :style="getReducerPosition(node)"
        @click.stop="selectNode(node)"
        @mousedown="startDragging($event, node)"
      >
        <div class="component-icon">
          <el-icon><Share /></el-icon>
        </div>
        <div class="component-label">{{ node.data.name }}</div>
      </div>
      
      <!-- 渲染弯头组件 -->
      <div
        v-for="node in getSpecialComponents('elbow')"
        :key="node.id"
        class="elbow-component"
        :class="{ selected: selectedNode === node.id }"
        :style="getElbowPosition(node)"
        @click.stop="selectNode(node)"
        @mousedown="startDragging($event, node)"
      >
        <div class="component-icon">
          <el-icon><Refresh /></el-icon>
        </div>
        <div class="component-label">{{ node.data.name }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DesignCanvas',
  props: {
    nodes: {
      type: Array,
      default: () => []
    },
    connections: {
      type: Array,
      default: () => []
    },
    selectedNode: {
      type: String,
      default: null
    },
    selectedConnection: {
      type: String,
      default: null
    },
    pipes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['add-node', 'update-node-position', 'select-node', 'select-connection', 'canvas-click'],
  data() {
    return {
      isDragging: false,
      draggedNode: null,
      dragOffset: { x: 0, y: 0 },
      connectMode: false,
      connectSource: null
    }
  },
  mounted() {
    // 添加全局鼠标移动和松开事件监听
    document.addEventListener('mousemove', this.onMouseMove)
    document.addEventListener('mouseup', this.onMouseUp)
  },
  beforeUnmount() {
    // 移除全局事件监听
    document.removeEventListener('mousemove', this.onMouseMove)
    document.removeEventListener('mouseup', this.onMouseUp)
  },
  methods: {
    // 处理拖放
    onDragOver(event) {
      event.preventDefault()
      event.dataTransfer.dropEffect = 'copy'
      console.log('拖动中...')
    },
    
    onDrop(event) {
      event.preventDefault()
      console.log('拖放事件被触发')
      try {
        // 获取拖拽数据
        const textData = event.dataTransfer.getData('text/plain');
        
        console.log('接收到的拖拽数据(text/plain):', textData);
        
        if (!textData) {
          console.error('未获取到拖拽数据');
          return;
        }
        
        // 解析数据
        let data;
        try {
          data = JSON.parse(textData);
        } catch (error) {
          console.error('解析拖拽数据失败:', error);
          return;
        }
        
        console.log('拖拽放置，接收到数据:', data);
        
        // 计算画布内的位置
        const canvasRect = this.$refs.canvasRef.getBoundingClientRect();
        const x = event.clientX - canvasRect.left;
        const y = event.clientY - canvasRect.top;
        
        // 更新位置
        data.position = { x, y };
        
        // 对于特殊组件（分离器、变径连接、弯头），检查是否放在管道上
        if (this.isSpecialComponent(data.type)) {
          const pipeUnderCursor = this.findPipeAtPosition(x, y);
          if (pipeUnderCursor) {
            data.data.target_pipe = pipeUnderCursor.id;
          } else {
            console.log('特殊组件需要放置在管道上');
            return;
          }
        }
        
        // 触发添加节点事件
        this.$emit('add-node', data);
      } catch (error) {
        console.error('处理拖拽事件失败:', error);
      }
    },
    
    // 获取节点标签
    getNodeLabel(node) {
      if (node.type === 'discharge_node') {
        return node.id
      } else if (node.type === 'flare_node') {
        return node.id
      } else if (node.type === 'normal_node') {
        return node.id
      } else if (node.type === 't_node') {
        return node.id
      }
      return node.id
    },
    
    // 获取管道标签
    getPipeLabel(connection) {
      const pipe = this.pipes.find(p => p.id === connection.id);
      if (!pipe) return '';
      
      // 显示管道标识
      let label = pipe.pipe_id || '';
      
      // 如果有直径和长度，添加这些信息
      if (pipe.diameter && pipe.equivalent_length) {
        label = `${label} (Ø${pipe.diameter}×${pipe.equivalent_length}mm)`;
      }
      
      return label;
    },
    
    // 计算管道标签位置
    getConnectionLabelPosition(connection) {
      const source = this.getNodePosition(connection.sourceId);
      const target = this.getNodePosition(connection.targetId);
      
      // 标签位置在连线中点
      return {
        x: (source.x + target.x) / 2,
        y: (source.y + target.y) / 2 - 10 // 稍微向上偏移，避免与线重叠
      };
    },
    
    // 获取节点位置
    getNodePosition(nodeId) {
      const node = this.nodes.find(n => n.id === nodeId)
      if (!node) return { x: 0, y: 0 }
      
      // 返回节点中心位置
      return {
        x: node.position.x + 20, // 节点宽度/2
        y: node.position.y + 20  // 节点高度/2
      }
    },
    
    // 开始拖拽节点
    startDragging(event, node) {
      if (event.button !== 0) return // 只处理左键
      
      this.isDragging = true
      this.draggedNode = node
      
      const rect = event.currentTarget.getBoundingClientRect()
      this.dragOffset = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      }
      
      // 阻止默认事件，防止文本选择等
      event.preventDefault()
    },
    
    // 处理鼠标移动
    onMouseMove(event) {
      if (!this.isDragging || !this.draggedNode) return
      
      const canvasRect = this.$refs.canvasRef.getBoundingClientRect()
      const x = Math.max(0, Math.min(event.clientX - canvasRect.left - this.dragOffset.x, canvasRect.width - 40))
      const y = Math.max(0, Math.min(event.clientY - canvasRect.top - this.dragOffset.y, canvasRect.height - 40))
      
      // 更新节点位置
      this.$emit('update-node-position', {
        id: this.draggedNode.id,
        position: { x, y }
      })
    },
    
    // 处理鼠标松开
    onMouseUp() {
      this.isDragging = false
      this.draggedNode = null
    },
    
    // 选择节点
    selectNode(node) {
      this.$emit('select-node', node.id)
    },
    
    // 选择连接
    selectConnection(connection) {
      this.$emit('select-connection', connection.id)
    },
    
    // 画布点击
    onCanvasClick() {
      this.$emit('canvas-click')
    },
    
    // 判断是否为特殊组件（分离器、变径连接、弯头）
    isSpecialComponent(type) {
      return ['separator', 'reducer', 'elbow'].includes(type);
    },
    
    // 获取特定类型的特殊组件
    getSpecialComponents(type) {
      return this.nodes.filter(node => node.type === type);
    },
    
    // 在指定位置查找管道
    findPipeAtPosition(x, y) {
      // 遍历所有连接，检查鼠标点击位置是否在管道附近
      for (const connection of this.connections) {
        const source = this.getNodePosition(connection.sourceId);
        const target = this.getNodePosition(connection.targetId);
        
        // 计算点到线段的距离
        const distance = this.pointToLineDistance(x, y, source.x, source.y, target.x, target.y);
        
        // 如果距离小于阈值（例如10像素），认为点击在管道上
        if (distance < 15) {
          return this.pipes.find(p => p.id === connection.id);
        }
      }
      
      return null;
    },
    
    // 计算点到线段的距离
    pointToLineDistance(px, py, x1, y1, x2, y2) {
      // 线段长度的平方
      const line_length_sq = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
      
      // 如果线段长度为0，直接返回点到端点的距离
      if (line_length_sq === 0) return Math.sqrt((px - x1) * (px - x1) + (py - y1) * (py - y1));
      
      // 计算投影点的参数t
      const t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_sq;
      
      // 如果t<0，最近点是第一个端点
      if (t < 0) return Math.sqrt((px - x1) * (px - x1) + (py - y1) * (py - y1));
      
      // 如果t>1，最近点是第二个端点
      if (t > 1) return Math.sqrt((px - x2) * (px - x2) + (py - y2) * (py - y2));
      
      // 计算投影点坐标
      const proj_x = x1 + t * (x2 - x1);
      const proj_y = y1 + t * (y2 - y1);
      
      // 返回点到投影点的距离
      return Math.sqrt((px - proj_x) * (px - proj_x) + (py - proj_y) * (py - proj_y));
    },
    
    // 获取分离器位置和旋转角度
    getSeparatorPosition(node) {
      if (!node.data.target_pipe) return { left: `${node.position.x}px`, top: `${node.position.y}px` };
      
      // 获取目标管道的连接
      const connection = this.connections.find(c => c.id === node.data.target_pipe);
      if (!connection) return { left: `${node.position.x}px`, top: `${node.position.y}px` };
      
      // 获取源节点和目标节点的位置
      const source = this.getNodePosition(connection.sourceId);
      const target = this.getNodePosition(connection.targetId);
      
      // 计算角度
      const angle = Math.atan2(target.y - source.y, target.x - source.x) * 180 / Math.PI;
      
      // 计算分离器在管道中间的位置
      const x = (source.x + target.x) / 2 - 30; // 30是组件宽度的一半
      const y = (source.y + target.y) / 2 - 15; // 15是组件高度的一半
      
      return {
        left: `${x}px`,
        top: `${y}px`,
        transform: `rotate(${angle}deg)`
      };
    },
    
    // 获取变径连接位置和旋转角度
    getReducerPosition(node) {
      if (!node.data.target_pipe) return { left: `${node.position.x}px`, top: `${node.position.y}px` };
      
      // 获取目标管道的连接
      const connection = this.connections.find(c => c.id === node.data.target_pipe);
      if (!connection) return { left: `${node.position.x}px`, top: `${node.position.y}px` };
      
      // 获取源节点和目标节点的位置
      const source = this.getNodePosition(connection.sourceId);
      const target = this.getNodePosition(connection.targetId);
      
      // 计算角度
      const angle = Math.atan2(target.y - source.y, target.x - source.x) * 180 / Math.PI;
      
      // 计算变径连接在管道中间的位置
      const x = (source.x + target.x) / 2 - 30; // 30是组件宽度的一半
      const y = (source.y + target.y) / 2 - 15; // 15是组件高度的一半
      
      return {
        left: `${x}px`,
        top: `${y}px`,
        transform: `rotate(${angle}deg)`
      };
    },
    
    // 获取弯头位置，并以90度角显示
    getElbowPosition(node) {
      if (!node.data.target_pipe) return { left: `${node.position.x}px`, top: `${node.position.y}px` };
      
      // 获取目标管道的连接
      const connection = this.connections.find(c => c.id === node.data.target_pipe);
      if (!connection) return { left: `${node.position.x}px`, top: `${node.position.y}px` };
      
      // 获取源节点和目标节点的位置
      const source = this.getNodePosition(connection.sourceId);
      const target = this.getNodePosition(connection.targetId);
      
      // 计算弯头位置 - 靠近目标节点
      const distanceRatio = 0.7; // 控制弯头在管道上的位置，0.5为中点，越大越靠近target
      const x = source.x + (target.x - source.x) * distanceRatio - 20; // 20是组件宽度的一半
      const y = source.y + (target.y - source.y) * distanceRatio - 20; // 20是组件高度的一半
      
      return {
        left: `${x}px`,
        top: `${y}px`
      };
    }
  }
}
</script>

<style scoped>
.design-canvas {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  flex: 1;
}

.canvas {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: #f5f7fa;
  background-image: linear-gradient(#e4e7ed 1px, transparent 1px),
                    linear-gradient(90deg, #e4e7ed 1px, transparent 1px);
  background-size: 20px 20px;
  flex: 1;
}

.node {
  position: absolute;
  width: 40px;
  height: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 50%;
  cursor: move;
  user-select: none;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.1s;
}

.node:hover {
  transform: scale(1.05);
}

.node.selected {
  box-shadow: 0 0 0 2px #409eff;
}

.node-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-label {
  position: absolute;
  bottom: -20px;
  font-size: 12px;
  white-space: nowrap;
}

.connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 5;
}

.connection-group {
  pointer-events: auto;
  cursor: pointer;
}

.connection-group line {
  transition: stroke-width 0.2s, stroke 0.2s;
}

.connection-group:hover line:not(.connection-hitbox) {
  stroke: #409eff;
  stroke-width: 3;
}

.connection-group.selected line:not(.connection-hitbox) {
  stroke: #409eff;
  stroke-width: 3;
}

.pipe-label {
  pointer-events: none;
  font-family: Arial, sans-serif;
  background-color: rgba(255, 255, 255, 0.7);
}

.connection-hitbox {
  opacity: 0;
}

.discharge_node {
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
  border-color: #f56c6c;
}

.flare_node {
  color: #e6a23c;
  background-color: rgba(230, 162, 60, 0.1);
  border-color: #e6a23c;
}

.normal_node {
  color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
  border-color: #409eff;
}

.t_node {
  color: #67c23a;
  background-color: rgba(103, 194, 58, 0.1);
  border-color: #67c23a;
}

/* 分离器样式 */
.separator-component {
  position: absolute;
  width: 60px;
  height: 30px;
  background-color: rgba(142, 68, 173, 0.1);
  border: 1px solid #8e44ad;
  color: #8e44ad;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: move;
  user-select: none;
  z-index: 8;
  transform-origin: center center;
}

.separator-component.selected {
  box-shadow: 0 0 0 2px #8e44ad;
}

/* 变径连接样式 */
.reducer-component {
  position: absolute;
  width: 60px;
  height: 30px;
  background-color: rgba(44, 62, 80, 0.1);
  border: 1px solid #2c3e50;
  color: #2c3e50;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: move;
  user-select: none;
  z-index: 8;
  transform-origin: center center;
}

.reducer-component.selected {
  box-shadow: 0 0 0 2px #2c3e50;
}

/* 弯头样式 */
.elbow-component {
  position: absolute;
  width: 40px;
  height: 40px;
  background-color: rgba(22, 160, 133, 0.1);
  border: 1px solid #16a085;
  color: #16a085;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: move;
  user-select: none;
  z-index: 8;
}

.elbow-component.selected {
  box-shadow: 0 0 0 2px #16a085;
}

.component-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.component-label {
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  text-align: center;
}
</style> 