<template>
  <div class="record-panel">
    <h3 class="panel-title">设计记录</h3>
    
    <!-- 保存记录按钮 -->
    <div class="save-record-section">
      <el-button type="primary" @click="openSaveDialog" size="default">
        <el-icon><Folder /></el-icon>
        保存记录
      </el-button>
    </div>
    
    <!-- 历史记录列表 -->
    <div class="history-records-section">
      <div class="section-header">
        <h4>历史记录</h4>
        <el-button type="text" @click="refreshRecords" size="small">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
      
      <el-scrollbar height="280px">
        <div v-if="loading" class="loading-placeholder">
          <el-skeleton :rows="3" animated />
        </div>
        
        <el-empty v-else-if="records.length === 0" description="暂无历史记录" />
        
        <div v-else class="records-list">
          <div
            v-for="record in records"
            :key="record.id"
            class="record-item"
            @click="loadRecord(record)"
          >
            <div class="record-time">
              {{ formatTime(record.record_time) }}
            </div>
            <div class="record-remark">
              {{ record.remark || '无备注' }}
            </div>
            <div class="record-path">
              {{ formatPath(record.local_path) }}
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>
    
    <!-- 保存记录对话框 -->
    <el-dialog
      v-model="saveDialogVisible"
      title="保存设计记录"
      width="500px"
    >
      <el-form :model="saveForm" label-position="top">
        <el-form-item label="保存路径">
          <el-input
            v-model="saveForm.local_path"
            placeholder="选择保存路径"
          >
            <template #append>
              <el-button @click="selectSavePath">
                <el-icon><FolderOpened /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="saveForm.remark"
            type="textarea"
            :rows="3"
            placeholder="输入备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="saveDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRecord" :loading="saving">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { flareApi } from '../api/flare-api';

export default {
  name: 'RecordPanel',
  props: {
    currentDesign: {
      type: Object,
      required: true
    }
  },
  emits: ['load-design'],
  setup(props, { emit }) {
    // 保存对话框相关状态
    const saveDialogVisible = ref(false);
    const saveForm = ref({
      local_path: localStorage.getItem('lastSavePath') || 'D:/FlareSystemDesigns',
      remark: ''
    });
    const saving = ref(false);
    
    // 历史记录相关状态
    const records = ref([]);
    const loading = ref(false);
    
    // 获取历史记录
    const fetchRecords = async () => {
      loading.value = true;
      try {
        const response = await flareApi.getRecordInfo();
        records.value = response.data.data || [];
      } catch (error) {
        console.error('获取历史记录失败:', error);
        ElMessage.error('获取历史记录失败');
      } finally {
        loading.value = false;
      }
    };
    
    // 加载记录
    const loadRecord = (record) => {
      ElMessageBox.confirm(
        `确定要加载"${record.remark || '未命名记录'}"吗？当前未保存的设计将会丢失。`,
        '加载历史记录',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        try {
          // 从本地文件加载设计数据
          const designData = loadDesignFromFile(record.local_path);
          
          // 通知父组件加载设计
          emit('load-design', designData);
          
          ElMessage.success('历史记录加载成功');
        } catch (error) {
          console.error('加载历史记录失败:', error);
          ElMessage.error('加载历史记录失败，文件可能已被移动或删除');
        }
      }).catch(() => {
        // 用户取消操作
      });
    };
    
    // 从本地文件加载设计数据
    const loadDesignFromFile = (filePath) => {
      try {
        // 此处应该用真实的文件读取逻辑替换
        // 由于浏览器安全限制，实际上需要配合桌面应用才能读取本地文件
        // 这里模拟从localStorage读取
        const savedData = localStorage.getItem(`design_${filePath}`);
        if (savedData) {
          return JSON.parse(savedData);
        }
        throw new Error('文件不存在');
      } catch (error) {
        console.error('读取设计文件失败:', error);
        throw error;
      }
    };
    
    // 刷新记录列表
    const refreshRecords = () => {
      fetchRecords();
    };
    
    // 打开保存对话框
    const openSaveDialog = () => {
      saveForm.value = {
        local_path: localStorage.getItem('lastSavePath') || 'D:/FlareSystemDesigns',
        remark: ''
      };
      saveDialogVisible.value = true;
    };
    
    // 选择保存路径
    const selectSavePath = () => {
      // 此处应该调用本地文件系统对话框
      // 由于浏览器安全限制，实际上需要配合桌面应用
      // 这里只是模拟路径选择
      const defaultPath = `D:/FlareSystemDesigns/design_${new Date().getTime()}.json`;
      saveForm.value.local_path = defaultPath;
    };
    
    // 保存记录
    const saveRecord = async () => {
      if (!saveForm.value.local_path) {
        ElMessage.warning('请选择保存路径');
        return;
      }
      
      saving.value = true;
      try {
        // 保存设计数据到本地文件
        saveDesignToLocal(props.currentDesign, saveForm.value.local_path);
        
        // 向后端发送记录信息
        const recordData = {
          record_time: new Date().toISOString(),
          local_path: saveForm.value.local_path,
          remark: saveForm.value.remark || ''
        };
        
        const response = await flareApi.saveRecord(recordData);
        
        // 保存成功后更新记录列表
        if (response.data.code === 'SUCCESS') {
          saveDialogVisible.value = false;
          ElMessage.success('设计记录保存成功');
          
          // 保存最后使用的路径
          localStorage.setItem('lastSavePath', saveForm.value.local_path);
          
          // 刷新记录列表
          fetchRecords();
        } else {
          throw new Error(response.data.message || '保存记录失败');
        }
      } catch (error) {
        console.error('保存记录失败:', error);
        ElMessage.error(`保存记录失败: ${error.message || '未知错误'}`);
      } finally {
        saving.value = false;
      }
    };
    
    // 保存设计到本地文件
    const saveDesignToLocal = (design, filePath) => {
      try {
        // 此处应该用真实的文件写入逻辑替换
        // 由于浏览器安全限制，实际上需要配合桌面应用才能写入本地文件
        // 这里模拟写入localStorage
        localStorage.setItem(`design_${filePath}`, JSON.stringify(design));
      } catch (error) {
        console.error('保存设计文件失败:', error);
        throw error;
      }
    };
    
    // 格式化时间显示
    const formatTime = (timeString) => {
      try {
        const date = new Date(timeString);
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
      } catch (error) {
        return timeString;
      }
    };
    
    // 格式化路径显示，只显示文件名部分
    const formatPath = (path) => {
      try {
        return path.split('/').pop();
      } catch (error) {
        return path;
      }
    };
    
    // 组件挂载时加载历史记录
    onMounted(() => {
      fetchRecords();
    });
    
    return {
      saveDialogVisible,
      saveForm,
      saving,
      records,
      loading,
      openSaveDialog,
      selectSavePath,
      saveRecord,
      refreshRecords,
      loadRecord,
      formatTime,
      formatPath
    };
  }
};
</script>

<style scoped>
.record-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 10px;
  box-sizing: border-box;
}

.panel-title {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  text-align: center;
}

.save-record-section {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
}

.history-records-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e0e0e0;
}

.section-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.loading-placeholder {
  padding: 16px;
}

.records-list {
  padding: 8px;
}

.record-item {
  padding: 10px;
  margin-bottom: 8px;
  background-color: white;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.record-item:hover {
  background-color: #f0f9ff;
  border-color: #a0cfff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.record-time {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.record-remark {
  color: #606266;
  margin-bottom: 4px;
}

.record-path {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style> 