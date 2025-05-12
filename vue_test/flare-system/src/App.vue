<script>
import { ref, reactive, computed } from 'vue'
import { toast } from 'vue3-toastify'
import NodeComponents from './components/NodeComponents.vue'
import DesignCanvas from './components/DesignCanvas.vue'
import PropertyPanel from './components/PropertyPanel.vue'
import ResultPanel from './components/ResultPanel.vue'
import RecordPanel from './components/RecordPanel.vue'
import { nodeUtils } from './utils/node-utils'
import { flareApi } from './api/flare-api'

export default {
  name: 'App',
  components: {
    NodeComponents,
    DesignCanvas,
    PropertyPanel,
    ResultPanel,
    RecordPanel
  },
  setup() {
    // 节点列表
    const nodes = ref([])
    
    // 管道列表
    const pipes = ref([])
    
    // 连接列表
    const connections = ref([])
    
    // 选中的节点和连接
    const selectedNodeId = ref(null)
    const selectedPipeId = ref(null)
    const selectedConnectionId = ref(null)
    
    // 连接模式
    const connectMode = ref(false)
    const connectSourceId = ref(null)
    
    // 检查结果
    const resultPanelVisible = ref(false)
    const loading = ref(false)
    const result = ref(null)
    const error = ref(null)
    
    // 方法：添加节点
    const addNode = (node) => {
      // 检查是否已存在火炬装置节点
      if (node.type === 'flare_node' && nodes.value.some(n => n.type === 'flare_node')) {
        toast.error('只能添加一个火炬装置节点')
        return
      }
      
      // 添加节点
      nodes.value.push(node)
      
      // 如果是管道节点，添加到管道列表
      if (node.type === 'pipe') {
        pipes.value.push({
          ...node.data,
          id: node.id
        })
      }
    }
    
    // 更新节点位置
    const updateNodePosition = ({ id, position }) => {
      const node = nodes.value.find(n => n.id === id)
      if (node) {
        node.position = position
      }
    }
    
    // 获取选中的节点
    const getSelectedNode = () => {
      return nodes.value.find(n => n.id === selectedNodeId.value)
    }
    
    // 获取选中的管道
    const getSelectedPipe = () => {
      return pipes.value.find(p => p.id === selectedPipeId.value)
    }
    
    // 选中节点
    const selectNode = (nodeId) => {
      if (connectMode.value) {
        // 在连接模式下，创建连接
        if (connectSourceId.value && connectSourceId.value !== nodeId) {
          createConnection(connectSourceId.value, nodeId)
          // 完成连接后重置连接模式
          connectMode.value = false
          connectSourceId.value = null
        } else {
          // 设置连接源节点
          connectSourceId.value = nodeId
        }
      } else {
        // 普通选择模式
        selectedNodeId.value = nodeId
        selectedPipeId.value = null
        selectedConnectionId.value = null
      }
    }
    
    // 更新节点
    const updateNode = (node) => {
      const index = nodes.value.findIndex(n => n.id === node.id)
      if (index !== -1) {
        nodes.value[index] = { ...node }
      }
    }
    
    // 更新管道
    const updatePipe = (pipe) => {
      const index = pipes.value.findIndex(p => p.id === pipe.id)
      if (index !== -1) {
        pipes.value[index] = { ...pipe }
      }
    }
    
    // 删除节点
    const removeNode = (nodeId) => {
      // 删除节点
      nodes.value = nodes.value.filter(n => n.id !== nodeId)
      
      // 删除与该节点相关的连接
      connections.value = connections.value.filter(
        c => c.sourceId !== nodeId && c.targetId !== nodeId
      )
      
      // 如果当前选中的是被删除的节点，取消选中
      if (selectedNodeId.value === nodeId) {
        selectedNodeId.value = null
      }
    }
    
    // 删除管道
    const removePipe = (pipeId) => {
      pipes.value = pipes.value.filter(p => p.id !== pipeId)
      if (selectedPipeId.value === pipeId) {
        selectedPipeId.value = null
      }
    }
    
    // 创建连接
    const createConnection = (sourceId, targetId) => {
      // 检查是否已存在相同的连接
      const existingConnection = connections.value.find(
        c => c.sourceId === sourceId && c.targetId === targetId ||
             c.sourceId === targetId && c.targetId === sourceId
      )
      
      if (existingConnection) {
        toast.warning('连接已存在')
        return
      }
      
      // 创建管道ID - 使用简单格式
      const pipeId = `${sourceId}->${targetId}`
      
      // 创建管道对象 - 使用源节点ID->目标节点ID作为pipe_id
      const pipe = {
        id: pipeId,
        pipe_id: pipeId,
        equivalent_length: 0,
        diameter: 0,
        roughness: 0.000045,
        cross_area: 0
      }
      
      // 添加连接和管道
      connections.value.push({
        id: pipeId,
        sourceId,
        targetId
      })
      
      pipes.value.push(pipe)
      
      // 提示成功
      toast.success('连接创建成功')
    }
    
    // 选择连接
    const selectConnection = (connectionId) => {
      selectedConnectionId.value = connectionId
      selectedNodeId.value = null
      selectedPipeId.value = connections.value.find(c => c.id === connectionId)?.id || null
    }
    
    // 删除连接
    const removeConnection = (connectionId) => {
      const connection = connections.value.find(c => c.id === connectionId)
      if (connection) {
        // 删除连接
        connections.value = connections.value.filter(c => c.id !== connectionId)
        
        // 删除对应的管道
        pipes.value = pipes.value.filter(p => p.id !== connectionId)
        
        // 重置选中状态
        if (selectedConnectionId.value === connectionId) {
          selectedConnectionId.value = null
        }
        
        if (selectedPipeId.value === connectionId) {
          selectedPipeId.value = null
        }
      }
    }
    
    // 切换连接模式
    const toggleConnectMode = () => {
      connectMode.value = !connectMode.value
      if (!connectMode.value) {
        connectSourceId.value = null
      } else {
        connectSourceId.value = selectedNodeId.value
      }
    }
    
    // 取消所有选择
    const deselectAll = () => {
      if (!connectMode.value) {
        selectedNodeId.value = null
        selectedPipeId.value = null
        selectedConnectionId.value = null
      }
    }
    
    // 检查系统
    const checkSystem = async () => {
      // 检查是否有足够的节点和连接
      if (nodes.value.length < 2 || connections.value.length < 1) {
        toast.error('请添加足够的节点和连接')
        return
      }
      
      // 检查是否存在火炬装置节点
      const flareNode = nodes.value.find(n => n.type === 'flare_node')
      if (!flareNode) {
        toast.error('请添加火炬装置节点')
        return
      }
      
      // 检查是否存在泄放点节点
      const dischargeNodes = nodes.value.filter(n => n.type === 'discharge_node')
      if (dischargeNodes.length === 0) {
        toast.error('请至少添加一个泄放点节点')
        return
      }
      
      // 检查泄放点和火炬是否连通
      // 这里简化处理，实际应该检查连通性
      
      // 准备API请求数据
      const requestData = nodeUtils.prepareApiData(nodes.value, connections.value, pipes.value)
      
      // 显示结果面板并加载
      resultPanelVisible.value = true
      loading.value = true
      result.value = null
      error.value = null
      
      try {
        const response = await flareApi.checkFlareSystem(requestData)
        result.value = response.data.result
        
        if (response.data.result.qualified) {
          toast.success('检查完成：系统符合安全要求')
        } else {
          toast.warning('检查完成：系统不符合安全要求')
        }
      } catch (err) {
        error.value = err.response?.data || { message: '检查失败，请稍后再试' }
        toast.error('检查失败：' + (error.value.message || '未知错误'))
      } finally {
        loading.value = false
      }
    }
    
    // 获取当前设计数据
    const getCurrentDesign = () => {
      return {
        nodes: nodes.value,
        connections: connections.value,
        pipes: pipes.value
      }
    }
    
    // 加载设计数据
    const loadDesign = (designData) => {
      // 清空当前设计
      nodes.value = []
      connections.value = []
      pipes.value = []
      
      // 加载新设计数据
      if (designData.nodes) {
        nodes.value = designData.nodes
      }
      
      if (designData.connections) {
        connections.value = designData.connections
      }
      
      if (designData.pipes) {
        pipes.value = designData.pipes
      }
      
      // 重置选中状态
      selectedNodeId.value = null
      selectedPipeId.value = null
      selectedConnectionId.value = null
      
      toast.success('设计数据加载成功')
    }
    
    return {
      nodes,
      pipes,
      connections,
      selectedNodeId,
      selectedPipeId,
      selectedConnectionId,
      connectMode,
      connectSourceId,
      resultPanelVisible,
      loading,
      result,
      error,
      addNode,
      updateNodePosition,
      getSelectedNode,
      getSelectedPipe,
      selectNode,
      updateNode,
      updatePipe,
      removeNode,
      removePipe,
      createConnection,
      selectConnection,
      removeConnection,
      toggleConnectMode,
      deselectAll,
      checkSystem,
      getCurrentDesign,
      loadDesign
    }
  }
}
</script>

<template>
  <div class="app-container">
    <el-container class="main-container">
      <el-header height="60px" class="app-header">
        <div class="header-logo">
          <el-icon><Aim /></el-icon>
          <h1>火炬管网系统设计计算</h1>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="checkSystem" size="large">
            <el-icon><Check /></el-icon>
            开始检查
          </el-button>
        </div>
      </el-header>
      
      <el-container class="content-container">
        <!-- 左侧面板 -->
        <el-aside width="200px" class="components-panel">
          <el-tabs type="border-card" style="height: 100%;">
            <el-tab-pane label="组件">
              <NodeComponents :nodes="nodes" @add-node="addNode" />
            </el-tab-pane>
            <el-tab-pane label="记录">
              <RecordPanel 
                :currentDesign="getCurrentDesign()" 
                @load-design="loadDesign" 
              />
            </el-tab-pane>
          </el-tabs>
        </el-aside>
        
        <!-- 中间设计区域 -->
        <el-main class="design-area">
          <DesignCanvas 
            :nodes="nodes"
            :connections="connections"
            :pipes="pipes"
            :selectedNode="getSelectedNode()"
            :selectedConnection="selectedConnectionId"
            @add-node="addNode"
            @update-node-position="updateNodePosition"
            @select-node="selectNode"
            @select-connection="selectConnection"
            @canvas-click="deselectAll"
          />
        </el-main>
        
        <!-- 右侧属性面板 -->
        <el-aside width="280px" class="properties-panel">
          <PropertyPanel 
            :selectedNode="getSelectedNode()"
            :selectedPipe="getSelectedPipe()"
            :selectedConnectionId="selectedConnectionId"
            :connectMode="connectMode"
            @update-node="updateNode"
            @update-pipe="updatePipe"
            @remove-node="removeNode"
            @remove-pipe="removePipe"
            @remove-connection="removeConnection"
            @toggle-connect-mode="toggleConnectMode"
          />
        </el-aside>
      </el-container>
    </el-container>
    
    <!-- 检查结果面板 -->
    <ResultPanel 
      :visible="resultPanelVisible"
      @update:visible="resultPanelVisible = $event"
      :loading="loading"
      :result="result"
      :error="error"
      @recheck="checkSystem"
    />
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#app {
  height: 100%;
  width: 100%;
}

.app-container {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.main-container {
  height: 100%;
  width: 100%;
}

.app-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header-logo {
  display: flex;
  align-items: center;
}

.header-logo h1 {
  margin: 0;
  margin-left: 10px;
  font-size: 20px;
}

.header-logo .el-icon {
  font-size: 24px;
}

.content-container {
  height: calc(100% - 60px);
  width: 100%;
  overflow: hidden;
  display: flex;
}

.components-panel {
  background-color: #f5f7fa;
  border-right: 1px solid #e0e0e0;
  overflow: hidden;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.components-panel :deep(.el-tabs) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.components-panel :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
  padding: 0;
}

.components-panel :deep(.el-tab-pane) {
  height: 100%;
  overflow: auto;
}

.properties-panel {
  background-color: #f5f7fa;
  border-left: 1px solid #e0e0e0;
  overflow-y: auto;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.05);
}

.design-area {
  padding: 0 !important;
  overflow: hidden;
  position: relative;
  flex: 1;
  display: flex;
}

/* 重置Element Plus样式 */
.el-header, .el-footer {
  padding: 0 !important;
}

.el-main {
  padding: 0 !important;
}

.el-aside {
  overflow: hidden !important;
}

.el-container {
  width: 100%;
  height: 100%;
}
</style>
