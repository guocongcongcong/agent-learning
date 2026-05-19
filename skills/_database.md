---
notion-bases: true
schema:
  - id: status
    name: 状态
    type: status
    visible: true
    width: 100
    options:
      - value: 待拆解
        color: '#868686'
      - value: 拆解中
        color: '#4ea6f5'
      - value: 已掌握
        color: '#4bb563'
  - id: source_project
    name: 来源项目
    type: text
    visible: true
    width: 200
  - id: complexity
    name: 复杂度
    type: select
    visible: true
    width: 100
    options:
      - value: low
        color: '#4bb563'
      - value: medium
        color: '#e8a138'
      - value: high
        color: '#e25555'
  - id: tags
    name: 标签
    type: multiselect
    visible: true
    width: 160
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
    hiddenColumns: []
    columnWidths: {}
  - id: board-status
    name: 拆解看板
    type: board
    filters: []
    sorts: []
    hiddenColumns: []
    columnWidths: {}
    groupByColumnId: status
---
