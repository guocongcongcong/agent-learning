---
notion-bases: true
schema:
  - id: order
    name: 顺序
    type: number
    visible: true
    width: 60
  - id: status
    name: 学习状态
    type: status
    visible: true
    width: 110
    options:
      - value: 未开始
        color: "#868686"
      - value: 学习中
        color: "#4ea6f5"
      - value: 已理解
        color: "#4bb563"
  - id: tags
    name: 标签
    type: multiselect
    visible: true
    width: 160
    options:
      - value: agent
      - value: skill
      - value: tool
      - value: mcp
      - value: context
      - value: harness
      - value: beginner
      - value: intermediate
      - value: advanced
  - id: confidence
    name: 可信度
    type: select
    visible: true
    width: 100
    options:
      - value: high
        color: "#4bb563"
      - value: medium
        color: "#e8a138"
      - value: low
        color: "#e25555"
  - id: created
    name: 创建
    type: date
    visible: true
    width: 100
  - id: updated
    name: 更新
    type: date
    visible: true
    width: 100
views:
  - id: default
    type: table
    filters: []
    sorts:
      - columnId: updated
        direction: desc
      - columnId: order
        direction: asc
    hiddenColumns: []
    columnWidths: {}
  - id: board-status
    name: 学习看板
    type: board
    filters: []
    sorts: []
    hiddenColumns: []
    columnWidths: {}
    groupByColumnId: status
---
