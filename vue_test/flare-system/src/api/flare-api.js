import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5000/api/v1/flare_system'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000
})

export const flareApi = {
  /**
   * 检查火炬系统是否符合要求
   * @param {Object} data - 系统配置和管道数据
   * @returns {Promise} - API响应
   */
  checkFlareSystem(data) {
    return apiClient.post('/check', data)
  },

  /**
   * 保存记录
   * @param {Object} data - 记录信息
   * @returns {Promise} - API响应
   */
  saveRecord(data) {
    return apiClient.post('/save', data)
  },

  /**
   * 获取历史记录信息
   * @returns {Promise} - API响应
   */
  getRecordInfo() {
    return apiClient.get('/info')
  }
}

export default flareApi 