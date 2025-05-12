<template>
  <div class="property-panel">
    <div v-if="!selectedNode && !selectedPipe && !selectedConnectionId" class="empty-panel">
      <el-empty description="选择节点或管道以编辑属性" />
    </div>
    
    <!-- 泄放点属性面板 -->
    <div v-if="selectedNode && selectedNode.type === 'discharge_node'" class="panel-content">
      <h3>泄放点属性</h3>
      <el-form label-position="top">
        <el-form-item label="泄放点ID">
          <el-input 
            v-model="selectedNode.data.node_id" 
            placeholder="输入泄放点ID"
            @input="updateNodeData"
          />
        </el-form-item>
        
        <el-form-item label="泄放量 (kg/h)">
          <el-input-number 
            v-model="selectedNode.data.flow_rate" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="泄放压力 (Pa)">
          <el-input-number 
            v-model="selectedNode.data.pressure" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="泄放温度 (K)">
          <el-input-number 
            v-model="selectedNode.data.temperature" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="分子量 (g/mol)">
          <el-input-number 
            v-model="selectedNode.data.molecular_weight" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="安全阀允许背压 (Pa)">
          <el-input-number 
            v-model="selectedNode.data.max_backpressure" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="泄放介质黏性 (Pa·s)">
          <el-input-number 
            v-model="selectedNode.data.viscosity" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 分离器属性面板 -->
    <div v-if="selectedNode && selectedNode.type === 'separator'" class="panel-content">
      <h3>分离器属性</h3>
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input 
            v-model="selectedNode.data.name" 
            placeholder="分离器名称"
            @input="updateNodeData"
          />
        </el-form-item>
        
        <el-form-item label="阻力系数">
          <el-input-number 
            v-model="selectedNode.data.resistance_coefficient" 
            :min="0"
            :precision="2"
            :step="0.1"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 变径连接属性面板 -->
    <div v-if="selectedNode && selectedNode.type === 'reducer'" class="panel-content">
      <h3>变径连接属性</h3>
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input 
            v-model="selectedNode.data.name" 
            placeholder="变径连接名称"
            @input="updateNodeData"
          />
        </el-form-item>
        
        <el-form-item label="入口内径 (mm)">
          <el-input-number 
            v-model="selectedNode.data.inlet_diameter" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="出口内径 (mm)">
          <el-input-number 
            v-model="selectedNode.data.outlet_diameter" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="长度 (mm)">
          <el-input-number 
            v-model="selectedNode.data.length" 
            :min="0"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="绝对粗糙度">
          <el-input-number 
            v-model="selectedNode.data.roughness" 
            :min="0"
            :precision="6"
            :step="0.000001"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 弯头属性面板 -->
    <div v-if="selectedNode && selectedNode.type === 'elbow'" class="panel-content">
      <h3>弯头属性</h3>
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input 
            v-model="selectedNode.data.name" 
            placeholder="弯头名称"
            @input="updateNodeData"
          />
        </el-form-item>
        
        <el-form-item label="阻力系数">
          <el-input-number 
            v-model="selectedNode.data.resistance_coefficient" 
            :min="0"
            :precision="2"
            :step="0.1"
            @change="updateNodeData"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 管道属性面板 -->
    <div v-if="selectedPipe" class="panel-content">
      <h3>管道属性
        <el-tag size="small" type="info" class="pipe-id-tag">
          {{ getPipeLabel(selectedPipe) }}
        </el-tag>
      </h3>
      <el-form label-position="top">
        <el-form-item label="管道ID">
          <el-input 
            v-model="selectedPipe.pipe_id" 
            disabled
          />
        </el-form-item>
        
        <el-form-item label="管道当量长度 (m)">
          <el-input-number 
            v-model="selectedPipe.equivalent_length" 
            :min="0"
            @change="updatePipeData"
            style="width: 100%"
            :controls-position="'right'"
          />
        </el-form-item>
        
        <el-form-item label="管道直径 (mm)">
          <el-input-number 
            v-model="selectedPipe.diameter" 
            :min="0"
            @change="updatePipeData"
            style="width: 100%"
            :controls-position="'right'"
          />
        </el-form-item>
        
        <el-form-item label="管道粗糙度">
          <el-input-number 
            v-model="selectedPipe.roughness" 
            :min="0"
            :precision="6"
            :step="0.000001"
            @change="updatePipeData"
            style="width: 100%"
            :controls-position="'right'"
          />
        </el-form-item>
        
        <el-form-item label="管道截面积 (cm²)">
          <el-input-number 
            v-model="selectedPipe.cross_area" 
            :min="0"
            @change="updatePipeData"
            style="width: 100%"
            :controls-position="'right'"
          />
        </el-form-item>
        
        <div class="auto-calculate-area">
          <el-alert
            type="info"
            show-icon
            :closable="false"
          >
            <template #title>
              <span>自动计算截面积</span>
            </template>
            <p>根据直径自动计算截面积</p>
            <el-button size="small" type="primary" @click="calculateArea">
              计算截面积
            </el-button>
          </el-alert>
        </div>
      </el-form>
    </div>
    
    <!-- 连接操作 -->
    <div v-if="!selectedNode && !selectedPipe && selectedConnectionId" class="panel-content">
      <h3>连接操作</h3>
      <el-button @click="removeConnection" type="danger" size="small">删除连接</el-button>
    </div>
    
    <!-- 节点操作 -->
    <div class="panel-actions" v-if="selectedNode || selectedPipe">
      <el-button @click="removeItem" type="danger" size="small">删除</el-button>
      
      <!-- 连接模式按钮，仅对节点显示（除了分离器、变径连接和弯头） -->
      <el-button 
        v-if="selectedNode && !isDisplayComponent(selectedNode.type)" 
        @click="toggleConnectMode" 
        type="primary" 
        size="small"
        :class="{ active: connectMode }"
      >
        {{ connectMode ? '取消连接' : '创建连接' }}
      </el-button>
    </div>
  </div>
</template>

<script>
import { nodeUtils } from '../utils/node-utils'

export default {
  name: 'PropertyPanel',
  props: {
    selectedNode: {
      type: Object,
      default: null
    },
    selectedPipe: {
      type: Object,
      default: null
    },
    selectedConnectionId: {
      type: String,
      default: null
    },
    connectMode: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'update-node', 
    'update-pipe', 
    'remove-node', 
    'remove-pipe', 
    'remove-connection', 
    'toggle-connect-mode'
  ],
  methods: {
    updateNodeData() {
      this.$emit('update-node', this.selectedNode)
    },
    
    updatePipeData() {
      this.$emit('update-pipe', this.selectedPipe)
    },
    
    removeItem() {
      if (this.selectedNode) {
        this.$emit('remove-node', this.selectedNode.id)
      } else if (this.selectedPipe) {
        this.$emit('remove-pipe', this.selectedPipe.id)
      }
    },
    
    removeConnection() {
      this.$emit('remove-connection', this.selectedConnectionId)
    },
    
    toggleConnectMode() {
      this.$emit('toggle-connect-mode')
    },
    
    // 判断是否为仅显示组件
    isDisplayComponent(type) {
      return ['separator', 'reducer', 'elbow'].includes(type);
    },
    
    // 根据直径自动计算截面积
    calculateArea() {
      if (!this.selectedPipe || !this.selectedPipe.diameter) {
        // 如果没有直径，弹出警告
        this.$message.warning('请先输入管道直径');
        return;
      }
      
      // 圆面积公式：π × (d/2)²
      const diameter = this.selectedPipe.diameter; // 单位：mm
      const radius = diameter / 2; // 单位：mm
      
      // 计算截面积，π × r²，单位转换为cm²（÷100）
      const area = Math.PI * Math.pow(radius, 2) / 100;
      
      // 更新管道截面积，保留2位小数
      this.selectedPipe.cross_area = parseFloat(area.toFixed(2));
      
      // 提交更新
      this.updatePipeData();
      
      // 提示用户计算成功
      this.$message.success(`截面积已计算: ${this.selectedPipe.cross_area} cm²`);
    },
    
    // 获取管道标签显示
    getPipeLabel(pipe) {
      if (!pipe) return '';
      return pipe.pipe_id;
    }
  }
}
</script>

<style scoped>
.property-panel {
  width: 100%;
  height: 100%;
  background-color: white;
  border-left: 1px solid #e0e0e0;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.empty-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.panel-content {
  margin-bottom: 20px;
}

.panel-content h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
}

.pipe-id-tag {
  margin-left: 8px;
  font-weight: normal;
}

.panel-actions {
  margin-top: auto;
  display: flex;
  gap: 10px;
}

.el-button.active {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
}

.el-form-item {
  margin-bottom: 18px;
}

:deep(.el-input-number) {
  width: 100%;
}

.auto-calculate-area {
  margin-top: 20px;
}

.auto-calculate-area p {
  margin: 8px 0;
  font-size: 12px;
  color: #666;
}

.component-info {
  margin-top: 20px;
  font-style: italic;
}
</style> 