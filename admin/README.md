# 火炬系统校验API服务

本项目提供了判断火炬装置是否符合规定的API服务。

## 功能简介

- 接收前端传输的装置参数和数据
- 进行计算和校验
- 返回装置是否符合规定的结论
- 提供记录保存功能
- 提供历史记录查询功能

## API接口

### 1. 判断装置是否符合规定接口

```
POST /api/v1/flare_system/check
```

#### 请求参数

```json
{
  "system_config": {
    "connection_graph": {
      "e": ["h"],
      "h": ["g"],
      "g": ["f", "i"],
      "i": ["d", "c"],
      "f": ["a", "b"]
    },
    "discharge_nodes": ["a", "b", "c", "d"],
    "flare_node": "e"
  },
  "pipes": [
    {
      "pipe_id": "a->f",
      "equivalent_length": 90.0,
      "diameter": 250.0,
      "roughness": 0.000045,
      "cross_area": 490.0
    },
    // 其他管道参数...
  ],
  "discharge_points": [
    {
      "node_id": "a",
      "flow_rate": 45360.0,
      "pressure": 2070000,
      "temperature": 338.0,
      "molecular_weight": 40.0,
      "max_backpressure": 307000,
      "viscosity": 0.000018
    },
    // 其他泄放点参数...
  ]
}
```

#### 返回示例

```json
{
  "status": 200,
  "message": "安全检查完成",
  "result": {
    "qualified": false,
    "check_time": "2025-05-01T14:30:45Z",
    "discharge_point_count": 4
  },
  "diagnostics": {
    "api_version": "天哥基础版",
    "calculation_cost": 0.45
  }
}
```

### 2. 记录保存接口

```
POST /api/v1/flare_system/save
```

#### 请求参数

```json
{
  "record_time": "2025-05-01T14:30:45Z",  // ISO8601格式
  "local_path": "D:\\Project\\FlareSystem\\Reports\\report.pdf",
  "remark": "季度审计报告-最终版"
}
```

#### 返回示例

```json
{
  "code": "SUCCESS",
  "message": "记录保存成功",
  "data": {
    "record_id": 1024,
    "created_at": "2025-05-01T14:30:46Z"
  }
}
```

### 3. 历史记录信息展示接口

```
GET /api/v1/flare_system/info
```

#### 返回示例

```json
{
  "data": [
    {
      "id": 1024,
      "record_time": "2025-05-01T14:30:45.123456Z",
      "local_path": "D:\\Project\\FlareSystem\\Reports\\report.pdf",
      "remark": "季度审计报告-最终版"
    },
    {
      "id": 1025,
      "record_time": "2025-05-01T15:30:45.123456Z",
      "local_path": "D:\\Project\\FlareSystem\\Reports\\report2.pdf",
      "remark": "安全检测报告"
    }
  ]
}
```

## 运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

## 技术栈

- Flask: Web框架
- PyMySQL: MySQL数据库连接
- 自研算法: 火炬系统校验计算逻辑 