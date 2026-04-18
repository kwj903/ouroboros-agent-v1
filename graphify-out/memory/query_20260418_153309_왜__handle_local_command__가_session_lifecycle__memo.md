---
type: "query"
date: "2026-04-18T15:33:09.969280+00:00"
question: "왜 _handle_local_command()가 Session Lifecycle, Memory and Logging, Approval Workflow, Session Service APIs를 연결하는가"
contributor: "graphify"
source_nodes: ["_handle_local_command()", "SessionState", "list_memory_suggestions()"]
---

# Q: 왜 _handle_local_command()가 Session Lifecycle, Memory and Logging, Approval Workflow, Session Service APIs를 연결하는가

## Answer

_handle_local_command()는 app/main.py의 로컬 CLI dispatcher로서 세션 전환/생성/삭제, 장기 기억 CRUD와 suggestion 처리, pending action 조회 및 approve/reject, 그리고 memory suggestion 서비스 표면과 겹치는 기능을 한 함수에서 분기한다. graphify에서 degree 28, high betweenness bridge로 나타났고, community 0 내부 세션 함수들과 community 1 memory 함수들, community 3 approval formatting, community 4 API memory suggestion surface를 함께 잇는다. 다만 community 1/3/4로 향하는 다수의 엣지는 INFERRED라서 구조적 사실과 클러스터 해석을 함께 봐야 한다.

## Source Nodes

- _handle_local_command()
- SessionState
- list_memory_suggestions()