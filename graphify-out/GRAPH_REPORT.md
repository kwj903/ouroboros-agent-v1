# Graph Report - /Users/kwj903/workspace/sandbox/free-model-test  (2026-04-19)

## Corpus Check
- 111 files · ~136,703 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 537 nodes · 993 edges · 57 communities detected
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 242 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Session Lifecycle|Session Lifecycle]]
- [[_COMMUNITY_Memory and Logging|Memory and Logging]]
- [[_COMMUNITY_API Session Actions|API Session Actions]]
- [[_COMMUNITY_Approval Workflow|Approval Workflow]]
- [[_COMMUNITY_Session Service APIs|Session Service APIs]]
- [[_COMMUNITY_Project Audit Docs|Project Audit Docs]]
- [[_COMMUNITY_Prompt Normalization|Prompt Normalization]]
- [[_COMMUNITY_Approval Workspace Flow|Approval Workspace Flow]]
- [[_COMMUNITY_Frontend HTML Shell|Frontend HTML Shell]]
- [[_COMMUNITY_CLI Command Surface|CLI Command Surface]]
- [[_COMMUNITY_Tool Trace Assembly|Tool Trace Assembly]]
- [[_COMMUNITY_Eval Assertions|Eval Assertions]]
- [[_COMMUNITY_Calculator Logic|Calculator Logic]]
- [[_COMMUNITY_API Schemas|API Schemas]]
- [[_COMMUNITY_UI Utility Hooks|UI Utility Hooks]]
- [[_COMMUNITY_Operations Sidebar|Operations Sidebar]]
- [[_COMMUNITY_App Favicon Mark|App Favicon Mark]]
- [[_COMMUNITY_Eval Run Comparison|Eval Run Comparison]]
- [[_COMMUNITY_Memory Eval Comparison|Memory Eval Comparison]]
- [[_COMMUNITY_Notes Search|Notes Search]]
- [[_COMMUNITY_Remote Ollama Client|Remote Ollama Client]]
- [[_COMMUNITY_Hero Illustration|Hero Illustration]]
- [[_COMMUNITY_React Logo Asset|React Logo Asset]]
- [[_COMMUNITY_Vite Logo Asset|Vite Logo Asset]]
- [[_COMMUNITY_Coverage Keyboard Icon|Coverage Keyboard Icon]]
- [[_COMMUNITY_Trace Analysis|Trace Analysis]]
- [[_COMMUNITY_Filesystem Paths|Filesystem Paths]]
- [[_COMMUNITY_Chat Panel Helpers|Chat Panel Helpers]]
- [[_COMMUNITY_Brand Social Icons|Brand Social Icons]]
- [[_COMMUNITY_Coverage Favicon|Coverage Favicon]]
- [[_COMMUNITY_Read Note Access|Read Note Access]]
- [[_COMMUNITY_Environment Settings|Environment Settings]]
- [[_COMMUNITY_SVG Sprite Reuse|SVG Sprite Reuse]]
- [[_COMMUNITY_Outlined Utility Icons|Outlined Utility Icons]]
- [[_COMMUNITY_Django Notes|Django Notes]]
- [[_COMMUNITY_React Compiler Guidance|React Compiler Guidance]]
- [[_COMMUNITY_Session Sidebar|Session Sidebar]]
- [[_COMMUNITY_Test Fixtures|Test Fixtures]]
- [[_COMMUNITY_Python Collections|Python Collections]]
- [[_COMMUNITY_Type Aware Linting|Type Aware Linting]]
- [[_COMMUNITY_React X Lint|React X Lint]]
- [[_COMMUNITY_React DOM Lint|React DOM Lint]]
- [[_COMMUNITY_Tool Registry|Tool Registry]]
- [[_COMMUNITY_ESLint Config|ESLint Config]]
- [[_COMMUNITY_Vite Config|Vite Config]]
- [[_COMMUNITY_React Entry Point|React Entry Point]]
- [[_COMMUNITY_Frontend Types|Frontend Types]]
- [[_COMMUNITY_Collapsible Section|Collapsible Section]]
- [[_COMMUNITY_Kilo Test|Kilo Test]]
- [[_COMMUNITY_Colab Test|Colab Test]]
- [[_COMMUNITY_LMStudio Test|LMStudio Test]]
- [[_COMMUNITY_OpenAI Test|OpenAI Test]]
- [[_COMMUNITY_Groq Test|Groq Test]]
- [[_COMMUNITY_Groq Test Two|Groq Test Two]]
- [[_COMMUNITY_OpenRouter Test Two|OpenRouter Test Two]]
- [[_COMMUNITY_Gemini Test|Gemini Test]]
- [[_COMMUNITY_OpenRouter Test|OpenRouter Test]]

## God Nodes (most connected - your core abstractions)
1. `SessionState` - 29 edges
2. `_handle_local_command()` - 28 edges
3. `request()` - 20 edges
4. `utc_now_iso()` - 17 edges
5. `run_agent()` - 17 edges
6. `main()` - 16 edges
7. `run_chat_turn()` - 15 edges
8. `generate_memory_suggestions()` - 14 edges
9. `refreshSessionView()` - 14 edges
10. `execute_pending_action()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Document Retrieval Step` --semantically_similar_to--> `Note File Discovery`  [INFERRED] [semantically similar]
  notes/rag_intro.md → htmlcov/z_9fc17fdde3804d40_search_notes_py.html
- `test_create_response_with_tools()` --calls--> `create_response()`  [INFERRED]
  tests/test_model.py → app/model.py
- `test_run_agent_basic()` --calls--> `run_agent()`  [INFERRED]
  tests/test_agent.py → app/agent.py
- `test_run_agent_with_tools()` --calls--> `run_agent()`  [INFERRED]
  tests/test_agent.py → app/agent.py
- `test_calculate_simple()` --calls--> `calculate()`  [INFERRED]
  tests/test_tools.py → app/tools/calculator.py

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

### Community 0 - "Session Lifecycle"
Cohesion: 0.08
Nodes (39): get_action(), create_new_session(), delete_session_by_id(), delete_session_choice(), format_session_list(), generate_session_id(), list_sessions(), _now_local_session_prefix() (+31 more)

### Community 1 - "Memory and Logging"
Cohesion: 0.08
Nodes (54): append_trace(), ensure_log_dir(), accept_memory_suggestion(), add_memory_note(), _append_record(), clear_memory_store(), configure_memory_store(), delete_memory_note() (+46 more)

### Community 2 - "API Session Actions"
Cohesion: 0.11
Nodes (44): approveAction(), createMemory(), createSession(), deleteMemory(), deleteSession(), dropMemorySuggestion(), fetchApprovals(), fetchMemories() (+36 more)

### Community 3 - "Approval Workflow"
Cohesion: 0.12
Nodes (38): create_pending_action(), _ensure_state_dir(), list_pending_actions(), _load_state(), mark_executed(), mark_failed(), mark_rejected(), _save_state() (+30 more)

### Community 4 - "Session Service APIs"
Cohesion: 0.07
Nodes (35): approve_action(), create_memory(), create_session(), delete_memory(), drop_memory_suggestion(), get_session_history(), get_session_tool_logs(), get_session_tool_panel() (+27 more)

### Community 5 - "Project Audit Docs"
Cohesion: 0.11
Nodes (27): Repository Operating Policy, Capability Mismatch Finding, Detailed Implementation Audit, Partial Implementation Audit, Detailed Project Handoff, Four-Tool Exposure Description, Handoff Next Work Items, Operational Source-of-Truth Guidance (+19 more)

### Community 6 - "Prompt Normalization"
Cohesion: 0.12
Nodes (20): build_system_prompt(), _debug_print(), _extract_pending_approval(), _format_pending_approval_message(), _normalize_cli_text(), _normalize_markdown_text(), _normalize_planner_tasks(), plan_tasks() (+12 more)

### Community 7 - "Approval Workspace Flow"
Cohesion: 0.1
Nodes (25): Human Approval Requirement, Approval-Mediated Tool Flow, File-Based Session State Store, Workspace Tools Layer, coverage.py v7.13.5, Answer Generation Step, Document Retrieval Step, Prompt Injection Step (+17 more)

### Community 8 - "Frontend HTML Shell"
Cohesion: 0.13
Nodes (16): favicon.svg, frontend Title, Frontend HTML Shell, src/main.tsx Entry Module, Responsive Viewport Meta Tag, Root Mount Container, ESLint Rules, HMR (+8 more)

### Community 9 - "CLI Command Surface"
Cohesion: 0.32
Nodes (14): build_parser(), cmd_api(), cmd_doctor(), cmd_frontend_build(), cmd_tui(), cmd_web(), _frontend_dev_url(), _frontend_dir() (+6 more)

### Community 10 - "Tool Trace Assembly"
Cohesion: 0.33
Nodes (12): _build_latest_execution(), _build_planner_log_entry(), build_tool_panel(), _classify_result_kind(), _extract_result_text(), _normalize_planner_tasks(), _parse_pending_approval(), _parse_plan_summary() (+4 more)

### Community 11 - "Eval Assertions"
Cohesion: 0.38
Nodes (9): check_contains(), check_forbidden(), check_tool_match(), extract_used_tools(), load_eval_cases(), main(), print_result(), run_single_eval() (+1 more)

### Community 12 - "Calculator Logic"
Cohesion: 0.36
Nodes (6): calculate(), _eval_node(), 안전한 사칙연산/거듭제곱 계산기.     예: '2 + 3 * (4 - 1)', test_calculate_complex(), test_calculate_error(), test_calculate_simple()

### Community 13 - "API Schemas"
Cohesion: 0.43
Nodes (7): BaseModel, ChatRequest, ChatResponse, CreateSessionResponse, MemoryCreateRequest, MemoryUpdateRequest, RenameSessionRequest

### Community 14 - "UI Utility Hooks"
Cohesion: 0.29
Nodes (2): getCellValue(), rowComparator()

### Community 15 - "Operations Sidebar"
Cohesion: 0.29
Nodes (0): 

### Community 16 - "App Favicon Mark"
Cohesion: 0.38
Nodes (7): Angular Bolt Mark, Browser Tab Branding, Lavender, Violet, and Cyan Accent Palette, Favicon Asset, Internal Glow Layers, Purple Primary Fill, Small-Size Recognition

### Community 17 - "Eval Run Comparison"
Cohesion: 0.6
Nodes (5): build_result_map(), compare_two_runs(), load_eval_runs(), main(), summarize_run()

### Community 18 - "Memory Eval Comparison"
Cohesion: 0.6
Nodes (5): build_result_map(), compare_two_runs(), load_memory_eval_runs(), main(), summarize_run()

### Community 19 - "Notes Search"
Cohesion: 0.53
Nodes (5): _iter_note_files(), _make_excerpt(), NOTES_DIR 아래의 .md, .txt 파일에서     query 키워드를 단순 검색해 관련도가 높은 파일을 반환한다., search_notes(), _tokenize()

### Community 20 - "Remote Ollama Client"
Cohesion: 0.33
Nodes (1): RemoteOllamaClient

### Community 21 - "Hero Illustration"
Cohesion: 0.33
Nodes (6): Hero PNG Asset, Centered White Tile, Landing Hero Visual, Layered Isometric Platform, Purple Glow Edge Lighting, Floating Top Panel

### Community 22 - "React Logo Asset"
Cohesion: 0.4
Nodes (6): Atom Orbit Motif, Central Nucleus, React Cyan Fill, Iconify Logos Collection, Non-text Brand Decoration, React Logo

### Community 23 - "Vite Logo Asset"
Cohesion: 0.33
Nodes (6): Central Lightning-Like Mark, Dark Mode Fill Swap, Purple-Cyan Glow Palette, Parenthesis Side Frame, Vite, Vite SVG Logo Asset

### Community 24 - "Coverage Keyboard Icon"
Cohesion: 0.47
Nodes (6): Closed Keyboard Icon Asset, Collapsed Panel State, HTML Coverage Report, Keyboard Icon, Keyboard Key Grid, Transparent Background

### Community 25 - "Trace Analysis"
Cohesion: 0.7
Nodes (4): load_traces(), main(), print_recent_runs(), summarize_traces()

### Community 26 - "Filesystem Paths"
Cohesion: 0.5
Nodes (2): _default_home_dir(), _expand()

### Community 27 - "Chat Panel Helpers"
Cohesion: 0.6
Nodes (3): getExecutionStatus(), getExecutionStatusLabel(), parsePendingApproval()

### Community 28 - "Brand Social Icons"
Cohesion: 0.4
Nodes (5): Bluesky Icon, Dark Brand Fill Style, Discord Icon, GitHub Icon, X Icon

### Community 29 - "Coverage Favicon"
Cohesion: 0.6
Nodes (5): 32px Coverage Favicon Asset, 32px Browser Favicon, HTML Coverage Report, Four-Segment Circular Swirl, Transparent Background

### Community 30 - "Read Note Access"
Cohesion: 0.67
Nodes (3): _is_within_notes_dir(), NOTES_DIR 아래의 특정 노트 파일 내용을 읽는다.     path는 반드시 NOTES_DIR 하위 파일이어야 한다., read_note()

### Community 31 - "Environment Settings"
Cohesion: 0.67
Nodes (0): 

### Community 32 - "SVG Sprite Reuse"
Cohesion: 0.67
Nodes (3): Frontend Icon Reuse, SVG Icon Sprite, SVG Symbol Sprite Pattern

### Community 33 - "Outlined Utility Icons"
Cohesion: 0.67
Nodes (3): Documentation Icon, Purple Outline Style, Social Icon

### Community 34 - "Django Notes"
Cohesion: 0.67
Nodes (3): Django, MTV Pattern, ORM

### Community 35 - "React Compiler Guidance"
Cohesion: 0.67
Nodes (3): React Compiler, React Compiler Installation Documentation, React Compiler disabled due to dev and build performance impact

### Community 36 - "Session Sidebar"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Test Fixtures"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Python Collections"
Cohesion: 1.0
Nodes (2): Python List, Python Tuple

### Community 39 - "Type Aware Linting"
Cohesion: 1.0
Nodes (2): Production applications should enable type-aware lint rules, Type-aware Lint Rules

### Community 40 - "React X Lint"
Cohesion: 1.0
Nodes (2): eslint-plugin-react-x, React-specific Lint Rules

### Community 41 - "React DOM Lint"
Cohesion: 1.0
Nodes (2): eslint-plugin-react-dom, React DOM Lint Rules

### Community 42 - "Tool Registry"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "ESLint Config"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Vite Config"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "React Entry Point"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Frontend Types"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Collapsible Section"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Kilo Test"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Colab Test"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "LMStudio Test"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "OpenAI Test"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Groq Test"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Groq Test Two"
Cohesion: 1.0
Nodes (0): 

### Community 54 - "OpenRouter Test Two"
Cohesion: 1.0
Nodes (0): 

### Community 55 - "Gemini Test"
Cohesion: 1.0
Nodes (0): 

### Community 56 - "OpenRouter Test"
Cohesion: 1.0
Nodes (0): 

## Ambiguous Edges - Review These
- `18-Tool Baseline` → `Four-Tool Exposure Description`  [AMBIGUOUS]
  PROJECT_HANDOFF_detailed.md · relation: conceptually_related_to

## Knowledge Gaps
- **65 isolated node(s):** `ALL의 OpenAI-compatible chat completion 호출`, `사용자의 요청을 분석해서 task list를 생성한다.`, `NOTES_DIR 아래의 .md, .txt 파일에서     query 키워드를 단순 검색해 관련도가 높은 파일을 반환한다.`, `안전한 사칙연산/거듭제곱 계산기.     예: '2 + 3 * (4 - 1)'`, `NOTES_DIR 아래의 특정 노트 파일 내용을 읽는다.     path는 반드시 NOTES_DIR 하위 파일이어야 한다.` (+60 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Session Sidebar`** (2 nodes): `SessionSidebar.tsx`, `SessionSidebar()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Test Fixtures`** (2 nodes): `test_data_dir()`, `conftest.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Python Collections`** (2 nodes): `Python List`, `Python Tuple`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Type Aware Linting`** (2 nodes): `Production applications should enable type-aware lint rules`, `Type-aware Lint Rules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `React X Lint`** (2 nodes): `eslint-plugin-react-x`, `React-specific Lint Rules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `React DOM Lint`** (2 nodes): `eslint-plugin-react-dom`, `React DOM Lint Rules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tool Registry`** (1 nodes): `tool_registry.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ESLint Config`** (1 nodes): `eslint.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite Config`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `React Entry Point`** (1 nodes): `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Frontend Types`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Collapsible Section`** (1 nodes): `CollapsibleSection.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kilo Test`** (1 nodes): `kilo_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Colab Test`** (1 nodes): `colab_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LMStudio Test`** (1 nodes): `lmstudio_server_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `OpenAI Test`** (1 nodes): `openai_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Groq Test`** (1 nodes): `groq_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Groq Test Two`** (1 nodes): `groq_test2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `OpenRouter Test Two`** (1 nodes): `openrouter_test2.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Gemini Test`** (1 nodes): `gemini_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `OpenRouter Test`** (1 nodes): `openrouter_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `18-Tool Baseline` and `Four-Tool Exposure Description`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `_handle_local_command()` connect `Session Lifecycle` to `Memory and Logging`, `Approval Workflow`, `Session Service APIs`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `utc_now_iso()` connect `Session Lifecycle` to `Memory and Logging`, `Approval Workflow`, `Prompt Normalization`, `Tool Trace Assembly`, `Eval Assertions`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `run_agent()` connect `Prompt Normalization` to `Session Lifecycle`, `Memory and Logging`, `Eval Assertions`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `SessionState` (e.g. with `_get_session_for_action()` and `_handle_local_command()`) actually correct?**
  _`SessionState` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `_handle_local_command()` (e.g. with `format_pending_actions()` and `list_recent_memory_notes()`) actually correct?**
  _`_handle_local_command()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `utc_now_iso()` (e.g. with `main()` and `create_pending_action()`) actually correct?**
  _`utc_now_iso()` has 16 INFERRED edges - model-reasoned connections that need verification._