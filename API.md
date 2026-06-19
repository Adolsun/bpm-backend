# BPM 后端 API 文档

> B站合集视频观看进度管理工具

**Base URL**: `http://localhost:8001`

---

## 合集管理

### 1. 创建合集

从B站API获取合集信息并保存到数据库。

**Endpoint**: `POST /collection`

**Request Body**:
```json
{
  "bvid": "BV1KsAWzNEUA"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| bvid | string | 是 | B站视频BV号 |

**Response** (201 Created):
```json
{
  "status": "success",
  "code": 200,
  "message": "合集创建成功",
  "data": {
    "season_id": 3041938,
    "title": "王者荣耀",
    "total_episodes": 635,
    "up_name": "磊哥游戏",
    "order_index": 0,
    "created_at": "2026-03-22T10:37:04",
    "updated_at": "2026-03-22T10:37:04",
    "last_sync_at": "2026-03-22T10:37:04",
    "videos": [
      {
        "bvid": "BV111421r75d",
        "title": "新英雄元流之子科研成果",
        "duration": 195,
        "collection_id": 3041938,
        "watched_count": 0,
        "order_index": 0,
        "status": "not_watched"
      }
    ]
  }
}
```

**Error Response** (400):
```json
{
  "detail": "该合集已存在，请勿重复添加"
}
```

---

### 2. 获取所有合集

返回所有合集及其包含的视频。

**Endpoint**: `GET /collection`

**Response** (200 OK):
```json
{
  "status": "success",
  "code": 200,
  "message": "获取所有合集信息成功",
  "data": [
    {
      "season_id": 3041938,
      "title": "王者荣耀",
      "total_episodes": 635,
      "up_name": "磊哥游戏",
      "order_index": 0,
      "created_at": "2026-03-22T10:37:04",
      "updated_at": "2026-03-22T10:37:04",
      "last_sync_at": "2026-03-22T10:37:04",
      "videos": [...]
    }
  ]
}
```

---

### 3. 删除单个合集

根据 season_id 删除指定合集。

**Endpoint**: `DELETE /collection/{season_id}`

**Path Parameters**:
| 参数 | 类型 | 说明 |
|------|------|------|
| season_id | integer | 合集ID |

**Response** (200 OK):
```json
{
  "status": "success",
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**Error Response** (404):
```json
{
  "detail": "合集不存在"
}
```

---

### 4. 批量删除合集

根据 season_id 列表批量删除合集。

**Endpoint**: `DELETE /collections`

**Request Body**:
```json
{
  "season_ids": [3041938, 6902742]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| season_ids | array[integer] | 是 | 合集ID列表 |

**Response** (200 OK):
```json
{
  "status": "success",
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 5. 更新合集

重新从B站API同步合集信息，同时保留原有视频的观看进度。

**Endpoint**: `POST /collection/update`

**Request Body**:
```json
{
  "season_id": 3041938
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| season_id | integer | 是 | 合集ID |

**Response** (200 OK):
```json
{
  "status": "success",
  "code": 200,
  "message": "合集更新成功",
  "data": {
    "season_id": 3041938,
    "title": "王者荣耀",
    ...
  }
}
```

---

### 6. 批量更新合集

批量重新同步多个合集的信息。

**Endpoint**: `POST /collections/batch-update`

**Request Body**:
```json
{
  "season_ids": [3041938, 6902742]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| season_ids | array[integer] | 是 | 合集ID列表 |

**Response** (200 OK):
```json
{
  "status": "success",
  "code": 200,
  "message": "批量更新完成，成功2个，失败0个",
  "data": {
    "succeeded": [
      {
        "season_id": 3041938,
        "status": "success",
        "data": {...}
      }
    ],
    "failed": []
  }
}
```

---

### 7. 合集排序

批量更新合集的排序顺序（用于拖拽排序）。

**Endpoint**: `PATCH /collection/order`

**Request Body**:
```json
{
  "updates": [
    { "season_id": 1, "order_index": 0 },
    { "season_id": 3, "order_index": 1 },
    { "season_id": 2, "order_index": 2 }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| updates | array[object] | 是 | 需要更新的排序列表 |
| updates[].season_id | integer | 是 | 合集的 season_id |
| updates[].order_index | integer | 是 | 新的排序值（越小越靠前） |

**Response** (200 OK):
```json
{
  "status": "success",
  "code": 200,
  "message": "排序更新成功，更新了 3 个合集",
  "data": null
}
```

---

## 视频管理

### 8. 更新视频观看状态

更新视频的观看次数和状态。

**Endpoint**: `PATCH /video`

**Request Body**:
```json
{
  "season_id": 3041938,
  "videos": [
    {
      "bvid": "BV111421r75d",
      "title": "新英雄元流之子科研成果",
      "duration": 195,
      "collection_id": 3041938,
      "watched_count": 0,
      "order_index": 0,
      "status": "not_watched"
    }
  ],
  "option": 1
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| season_id | integer | 是 | 合集ID |
| videos | array[Video] | 是 | 视频列表 |
| option | integer | 是 | 操作类型：0=标记为已看、1=观看次数+1、2=观看次数-1 |

**option 说明**:
- `0`: 将所有观看次数为0的视频标记为"部分观看"
- `1`: 所有视频观看次数+1，状态改为"已看完"
- `2`: 所有视频观看次数-1，如果为0则改回"未看"

**Response** (200 OK):
```json
{
  "status": "success",
  "code": 200,
  "message": "获取合集信息成功",
  "data": {
    "season_id": 3041938,
    "title": "王者荣耀",
    "videos": [...]
  }
}
```

**Error Response** (400):
```json
{
  "detail": "非法option"
}
```

---

## 数据模型

### Collection (合集)
| 字段 | 类型 | 说明 |
|------|------|------|
| season_id | integer | 合集ID（主键） |
| title | string | 合集标题 |
| total_episodes | integer | 视频总集数 |
| up_name | string | UP主名称 |
| order_index | integer | 排序索引（用于拖动排序） |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 最后修改时间 |
| last_sync_at | datetime | 最后同步时间 |

### Video (视频)
| 字段 | 类型 | 说明 |
|------|------|------|
| bvid | string | BV号（主键） |
| title | string | 视频标题 |
| duration | integer | 视频时长（秒） |
| collection_id | integer | 所属合集ID |
| watched_count | integer | 观看次数 |
| order_index | integer | 排序索引 |
| status | string | 观看状态：`not_watched` / `watched` / `partially_watched` |

---

## 通用响应格式

**成功**:
```json
{
  "status": "success",
  "code": 200,
  "message": "操作描述",
  "data": {...}
}
```

**错误**:
```json
{
  "detail": "错误描述"
}
```

---

## 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |