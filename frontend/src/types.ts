export type SessionItem = {
  session_id: string
  created_at?: string
  updated_at?: string
  title?: string
}

export type ChatMessage = {
  role: "user" | "assistant"
  content: string
}

export type ChatResponse = {
  session_id: string
  answer: string
  status: string
  action_id: string | null
  action_required: boolean
  action_summary: string | null
  suggestions_created: number
}

export type ApprovalItem = {
  action_id: string
  action_type: string
  summary: string
  session_id?: string | null
  status: string
  created_at?: string
  updated_at?: string
  payload?: Record<string, unknown>
}

export type MemoryItem = {
  memory_id: string
  timestamp: string
  content: string
  tags: string[]
  importance: number
  note_type: string
  source_session_id?: string | null
}

export type MemorySuggestionItem = {
  suggestion_id: string
  timestamp: string
  source_session_id?: string | null
  source_role: string
  content: string
  tags: string[]
  importance: number
  note_type: string
  status: string
}

export type WorkspaceState = {
  last_browsed_path?: string
  last_read_path?: string
  last_search_query?: string
  last_search_path?: string
  last_requested_write_path?: string
  last_requested_modify_path?: string
  last_requested_delete_path?: string
  last_requested_create_path?: string
  last_pending_action_id?: string | null
  last_pending_summary?: string | null
  last_action_id?: string
  last_action_type?: string
  last_action_status?: string
  last_written_path?: string
  last_created_path?: string
  last_modified_path?: string
  last_deleted_path?: string
}

export type ToolLogItem = {
  timestamp: string
  step_index: number
  tool_name: string
  arguments: Record<string, unknown>
  result_preview: string
  result_raw: string
}

export type ToolPanelSearchItem = {
  path?: string
  score?: string
  preview?: string
  raw: string
}

export type ToolPanelReadItem = {
  path?: string | null
  content_preview: string
  raw: string
}

export type ToolPanelData = {
  last_note_search: {
    query?: string | null
    items: ToolPanelSearchItem[]
    raw: string
  } | null
  last_note_read: ToolPanelReadItem | null
  last_file_read: ToolPanelReadItem | null
}
