<template>
  <div class="result-panel">
    <el-drawer
      :model-value="visible"
      @update:model-value="$emit('update:visible', $event)"
      title="检查结果"
      size="40%"
      direction="rtl"
    >
      <template #header>
        <h3 class="result-title">
          <el-icon class="icon" :class="{ success: isSuccessful, error: !isSuccessful }">
            <component :is="isSuccessful ? 'SuccessFilled' : 'CircleCloseFilled'" />
          </el-icon>
          检查结果
        </h3>
      </template>
      
      <!-- 加载中 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>
      
      <!-- 结果内容 -->
      <div v-else-if="result" class="result-content">
        <div class="result-header" :class="{ success: isSuccessful, error: !isSuccessful }">
          <el-alert
            :title="isSuccessful ? '系统符合安全要求' : '系统不符合安全要求'"
            :type="isSuccessful ? 'success' : 'error'"
            :description="getResultDescription()"
            :closable="false"
            show-icon
          />
        </div>
        
        <div class="result-details">
          <el-descriptions title="检查详情" :column="1" border>
            <el-descriptions-item label="检查时间">
              {{ formatDate(result.check_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="泄放点数量">
              {{ result.discharge_point_count }}
            </el-descriptions-item>
            <el-descriptions-item label="检查版本">
              {{ result.api_version || '默认版本' }}
            </el-descriptions-item>
            <el-descriptions-item label="计算耗时">
              {{ result.calculation_cost || 0 }} 秒
            </el-descriptions-item>
          </el-descriptions>
          
          <!-- 错误信息 -->
          <div v-if="error" class="error-message">
            <el-alert
              :title="error.message || '未知错误'"
              type="error"
              :description="`错误代码: ${error.error_code || '未知'}`"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-result">
        <el-empty description="尚未进行检查" />
      </div>
      
      <!-- 底部按钮 -->
      <template #footer>
        <div class="footer-buttons">
          <el-button @click="close">关闭</el-button>
          <el-button type="primary" @click="recheck">重新检查</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script>
export default {
  name: 'ResultPanel',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    result: {
      type: Object,
      default: null
    },
    error: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible', 'recheck'],
  computed: {
    isSuccessful() {
      return this.result && this.result.qualified === true
    }
  },
  methods: {
    close() {
      this.$emit('update:visible', false)
    },
    
    recheck() {
      this.$emit('recheck')
    },
    
    formatDate(dateString) {
      if (!dateString) return '未知时间'
      
      try {
        const date = new Date(dateString)
        return date.toLocaleString('zh-CN')
      } catch (error) {
        return dateString
      }
    },
    
    getResultDescription() {
      if (this.isSuccessful) {
        return '火炬系统设计符合安全要求，所有泄放点的入口压力均低于允许背压'
      } else {
        return '火炬系统设计不符合安全要求，存在泄放点入口压力超过允许背压'
      }
    }
  }
}
</script>

<style scoped>
.result-title {
  display: flex;
  align-items: center;
  margin: 0;
  font-size: 18px;
}

.result-title .icon {
  margin-right: 10px;
  font-size: 20px;
}

.icon.success {
  color: #67c23a;
}

.icon.error {
  color: #f56c6c;
}

.loading-container {
  padding: 20px;
}

.result-content {
  padding: 0 20px;
}

.result-header {
  margin-bottom: 20px;
}

.result-details {
  margin-top: 20px;
}

.error-message {
  margin-top: 20px;
}

.empty-result {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.footer-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 