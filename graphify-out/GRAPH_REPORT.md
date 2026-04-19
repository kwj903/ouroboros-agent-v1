# Graph Report - /Users/kwj903/workspace/sandbox/free-model-test  (2026-04-19)

## Corpus Check
- 55 files · ~179,780 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 532 nodes · 995 edges · 61 communities detected
- Extraction: 75% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 243 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]

## God Nodes (most connected - your core abstractions)
1. `SessionState` - 29 edges
2. `_handle_local_command()` - 28 edges
3. `run_agent()` - 21 edges
4. `request()` - 20 edges
5. `utc_now_iso()` - 17 edges
6. `main()` - 16 edges
7. `run_chat_turn()` - 15 edges
8. `refreshSessionView()` - 15 edges
9. `generate_memory_suggestions()` - 14 edges
10. `execute_pending_action()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `run_agent()`  [INFERRED]
  app/main.py → /Users/kwj903/workspace/sandbox/free-model-test/app/agent.py
- `main()` --calls--> `run_agent()`  [INFERRED]
  app/preview_markdown.py → /Users/kwj903/workspace/sandbox/free-model-test/app/agent.py
- `_build_planner_log_entry()` --calls--> `utc_now_iso()`  [INFERRED]
  /Users/kwj903/workspace/sandbox/free-model-test/app/tool_trace_manager.py → app/logger.py
- `persist_tool_trace()` --calls--> `utc_now_iso()`  [INFERRED]
  /Users/kwj903/workspace/sandbox/free-model-test/app/tool_trace_manager.py → app/logger.py
- `persist_tool_trace()` --calls--> `run_chat_turn()`  [INFERRED]
  /Users/kwj903/workspace/sandbox/free-model-test/app/tool_trace_manager.py → app/api/services.py

## Hyperedges (group relationships)
- **Favicon Mark Composition** — favicon_favicon_asset, favicon_angular_bolt_mark, favicon_internal_glow_layers [INFERRED 0.88]
- **Sprite Symbol Collection** — icons_icon_sprite, icons_bluesky_icon, icons_discord_icon, icons_documentation_icon, icons_github_icon, icons_social_icon, icons_x_icon [EXTRACTED 1.00]
- **Dark Filled Brand Icons** — icons_bluesky_icon, icons_discord_icon, icons_github_icon, icons_x_icon, icons_dark_brand_fill_style [EXTRACTED 1.00]
- **Purple Outlined Utility Icons** — icons_documentation_icon, icons_social_icon, icons_purple_outline_style [EXTRACTED 1.00]
- **Stacked Hero Composition** — hero_layered_platform, hero_top_panel, hero_center_tile, hero_purple_glow_edge [EXTRACTED 1.00]
- **React Logo Composition** — react_react_logo, react_atom_orbit_motif, react_central_nucleus [INFERRED 0.88]
- **Vite Logo Lockup** — vite_vite_logo_asset, vite_central_lightning_mark, vite_parenthesis_side_frame [EXTRACTED 1.00]
- **Ouroboros Runtime Stack** — docs_PRODUCT_ouroboros_project, docs_ARCHITECTURE_agent_core_module, docs_ARCHITECTURE_approval_mediated_tool_flow, docs_PRODUCT_dual_interface_strategy [INFERRED 0.86]
- **Workspace Approval Cycle** — z_9fc17fdde3804d40_approval_request_tool_set, z_9fc17fdde3804d40_pending_action_executor, docs_ARCHITECTURE_approval_mediated_tool_flow [INFERRED 0.92]
- **Note Search Pipeline** — z_9fc17fdde3804d40_search_notes_tool, z_9fc17fdde3804d40_search_notes_note_file_discovery, z_9fc17fdde3804d40_search_notes_keyword_scoring, z_9fc17fdde3804d40_search_notes_excerpt_builder [EXTRACTED 1.00]
- **Frontend Bootstrap Form** — index_html_shell, index_root_mount_container, index_main_tsx_entry_module [INFERRED 0.84]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (52): accept_memory_suggestion(), add_memory_note(), _append_record(), clear_memory_store(), configure_memory_store(), delete_memory_note(), delete_memory_note_tool(), dismiss_memory_suggestion() (+44 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (33): get_action(), create_new_session(), delete_session_by_id(), delete_session_choice(), format_session_list(), generate_session_id(), list_sessions(), _now_local_session_prefix() (+25 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (45): approveAction(), createMemory(), createSession(), deleteMemory(), deleteSession(), dropMemorySuggestion(), fetchApprovals(), fetchMemories() (+37 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (40): approve_action(), chat(), create_memory(), create_session(), delete_memory(), delete_session(), drop_memory_suggestion(), get_session_history() (+32 more)

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (39): create_pending_action(), _ensure_state_dir(), list_pending_actions(), _load_state(), mark_executed(), mark_failed(), mark_rejected(), _save_state() (+31 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (30): build_system_prompt(), _count_action_categories(), _debug_print(), _extract_pending_approval(), _format_pending_approval_message(), _has_multiple_instruction_lines(), _matches_any(), _normalize_cli_text() (+22 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (31): Human Approval Requirement, Repository Operating Policy, Capability Mismatch Finding, Detailed Implementation Audit, Partial Implementation Audit, Detailed Project Handoff, Four-Tool Exposure Description, Handoff Next Work Items (+23 more)

### Community 7 - "Community 7"
Cohesion: 0.32
Nodes (14): build_parser(), cmd_api(), cmd_doctor(), cmd_frontend_build(), cmd_tui(), cmd_web(), _frontend_dev_url(), _frontend_dir() (+6 more)

### Community 8 - "Community 8"
Cohesion: 0.27
Nodes (11): check_contains(), check_forbidden(), check_tool_match(), extract_used_tools(), load_eval_cases(), main(), print_result(), run_single_eval() (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (12): _build_latest_execution(), _build_planner_log_entry(), build_tool_panel(), _classify_result_kind(), _extract_result_text(), _normalize_planner_tasks(), _parse_pending_approval(), _parse_plan_summary() (+4 more)

### Community 10 - "Community 10"
Cohesion: 0.2
Nodes (10): ESLint Rules, HMR, Oxc, React, React + TypeScript + Vite Template, SWC, TypeScript, Vite (+2 more)

### Community 11 - "Community 11"
Cohesion: 0.36
Nodes (6): calculate(), _eval_node(), 안전한 사칙연산/거듭제곱 계산기.     예: '2 + 3 * (4 - 1)', test_calculate_complex(), test_calculate_error(), test_calculate_simple()

### Community 12 - "Community 12"
Cohesion: 0.43
Nodes (7): BaseModel, ChatRequest, ChatResponse, CreateSessionResponse, MemoryCreateRequest, MemoryUpdateRequest, RenameSessionRequest

### Community 13 - "Community 13"
Cohesion: 0.29
Nodes (2): getCellValue(), rowComparator()

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 0.38
Nodes (7): Angular Bolt Mark, Browser Tab Branding, Lavender, Violet, and Cyan Accent Palette, Favicon Asset, Internal Glow Layers, Purple Primary Fill, Small-Size Recognition

### Community 16 - "Community 16"
Cohesion: 0.6
Nodes (5): build_result_map(), compare_two_runs(), load_eval_runs(), main(), summarize_run()

### Community 17 - "Community 17"
Cohesion: 0.6
Nodes (5): build_result_map(), compare_two_runs(), load_memory_eval_runs(), main(), summarize_run()

### Community 18 - "Community 18"
Cohesion: 0.53
Nodes (5): _iter_note_files(), _make_excerpt(), NOTES_DIR 아래의 .md, .txt 파일에서     query 키워드를 단순 검색해 관련도가 높은 파일을 반환한다., search_notes(), _tokenize()

### Community 19 - "Community 19"
Cohesion: 0.33
Nodes (1): RemoteOllamaClient

### Community 20 - "Community 20"
Cohesion: 0.33
Nodes (6): Hero PNG Asset, Centered White Tile, Landing Hero Visual, Layered Isometric Platform, Purple Glow Edge Lighting, Floating Top Panel

### Community 21 - "Community 21"
Cohesion: 0.4
Nodes (6): Atom Orbit Motif, Central Nucleus, React Cyan Fill, Iconify Logos Collection, Non-text Brand Decoration, React Logo

### Community 22 - "Community 22"
Cohesion: 0.33
Nodes (6): Central Lightning-Like Mark, Dark Mode Fill Swap, Purple-Cyan Glow Palette, Parenthesis Side Frame, Vite, Vite SVG Logo Asset

### Community 23 - "Community 23"
Cohesion: 0.47
Nodes (6): Closed Keyboard Icon Asset, Collapsed Panel State, HTML Coverage Report, Keyboard Icon, Keyboard Key Grid, Transparent Background

### Community 24 - "Community 24"
Cohesion: 0.7
Nodes (4): load_traces(), main(), print_recent_runs(), summarize_traces()

### Community 25 - "Community 25"
Cohesion: 0.5
Nodes (2): _default_home_dir(), _expand()

### Community 26 - "Community 26"
Cohesion: 0.6
Nodes (3): getExecutionStatus(), getExecutionStatusLabel(), parsePendingApproval()

### Community 27 - "Community 27"
Cohesion: 0.4
Nodes (5): Bluesky Icon, Dark Brand Fill Style, Discord Icon, GitHub Icon, X Icon

### Community 28 - "Community 28"
Cohesion: 0.6
Nodes (5): 32px Coverage Favicon Asset, 32px Browser Favicon, HTML Coverage Report, Four-Segment Circular Swirl, Transparent Background

### Community 29 - "Community 29"
Cohesion: 0.67
Nodes (3): _is_within_notes_dir(), NOTES_DIR 아래의 특정 노트 파일 내용을 읽는다.     path는 반드시 NOTES_DIR 하위 파일이어야 한다., read_note()

### Community 30 - "Community 30"
Cohesion: 0.5
Nodes (4): Answer Generation Step, Document Retrieval Step, Prompt Injection Step, Retrieval-Augmented Generation

### Community 31 - "Community 31"
Cohesion: 0.67
Nodes (0): 

### Community 32 - "Community 32"
Cohesion: 0.67
Nodes (3): Documentation Icon, Purple Outline Style, Social Icon

### Community 33 - "Community 33"
Cohesion: 0.67
Nodes (3): Frontend Icon Reuse, SVG Icon Sprite, SVG Symbol Sprite Pattern

### Community 34 - "Community 34"
Cohesion: 0.67
Nodes (3): Django, MTV Pattern, ORM

### Community 35 - "Community 35"
Cohesion: 0.67
Nodes (3): coverage.py v7.13.5, search_notes Coverage Report, workspace_tools Coverage Report

### Community 36 - "Community 36"
Cohesion: 0.67
Nodes (3): React Compiler, React Compiler Installation Documentation, React Compiler disabled due to dev and build performance impact

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (2): Python List, Python Tuple

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (2): read_note vs workspace_tools Boundary, Tool Overlap Review Request

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (2): Production applications should enable type-aware lint rules, Type-aware Lint Rules

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (2): eslint-plugin-react-x, React-specific Lint Rules

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (2): eslint-plugin-react-dom, React DOM Lint Rules

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (0): 

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (0): 

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (0): 

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (0): 

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (0): 

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (0): 

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): 사용자의 요청을 분석해서 task list를 생성한다.

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Batch File Creation Request

## Ambiguous Edges - Review These
- `18-Tool Baseline` → `Four-Tool Exposure Description`  [AMBIGUOUS]
  PROJECT_HANDOFF_detailed.md · relation: conceptually_related_to

## Knowledge Gaps
- **68 isolated node(s):** `ALL의 OpenAI-compatible chat completion 호출`, `복합/다단계 요청에서만 planner LLM 호출을 사용한다.`, `사용자의 요청을 분석해서 task list를 생성한다.`, `NOTES_DIR 아래의 .md, .txt 파일에서     query 키워드를 단순 검색해 관련도가 높은 파일을 반환한다.`, `안전한 사칙연산/거듭제곱 계산기.     예: '2 + 3 * (4 - 1)'` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 37`** (2 nodes): `SessionSidebar.tsx`, `SessionSidebar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `test_data_dir()`, `conftest.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `Python List`, `Python Tuple`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (2 nodes): `read_note vs workspace_tools Boundary`, `Tool Overlap Review Request`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `Production applications should enable type-aware lint rules`, `Type-aware Lint Rules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (2 nodes): `eslint-plugin-react-x`, `React-specific Lint Rules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (2 nodes): `eslint-plugin-react-dom`, `React DOM Lint Rules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `tool_registry.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `eslint.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `CollapsibleSection.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `kilo_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `colab_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `lmstudio_server_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `openai_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `groq_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `groq_test2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `openrouter_test2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `gemini_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `openrouter_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `사용자의 요청을 분석해서 task list를 생성한다.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Batch File Creation Request`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `18-Tool Baseline` and `Four-Tool Exposure Description`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `run_agent()` connect `Community 5` to `Community 8`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `_handle_local_command()` connect `Community 1` to `Community 0`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `utc_now_iso()` connect `Community 1` to `Community 0`, `Community 4`, `Community 5`, `Community 8`, `Community 9`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `SessionState` (e.g. with `_get_session_for_action()` and `_handle_local_command()`) actually correct?**
  _`SessionState` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `_handle_local_command()` (e.g. with `format_pending_actions()` and `list_recent_memory_notes()`) actually correct?**
  _`_handle_local_command()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `run_agent()` (e.g. with `main()` and `utc_now_iso()`) actually correct?**
  _`run_agent()` has 12 INFERRED edges - model-reasoned connections that need verification._