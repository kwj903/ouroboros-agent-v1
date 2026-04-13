import type {
  ApprovalItem,
  ChatMessage,
  ChatResponse,
  MemoryItem,
  MemorySuggestionItem,
  SessionItem,
  WorkspaceState,
  ToolLogItem,
  ToolPanelData,
} from "./types"

const BASE_URL = "http://127.0.0.1:8000"


export async function fetchSessionWorkspaceState(
  sessionId: string,
): Promise<WorkspaceState> {
  return request<WorkspaceState>(`/sessions/${sessionId}/workspace-state`)
}


async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`API ${response.status}: ${text}`)
  }

  return response.json() as Promise<T>
}

export async function fetchSessions(): Promise<SessionItem[]> {
  return request<SessionItem[]>("/sessions")
}

export async function createSession(): Promise<{ session_id: string; title: string }> {
  return request("/sessions", {
    method: "POST",
  })
}

export async function sendChat(params: {
  message: string
  session_id?: string | null
  output_mode?: "cli" | "markdown"
  response_language?: "ko" | "en"
}): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({
      message: params.message,
      session_id: params.session_id ?? null,
      output_mode: params.output_mode ?? "markdown",
      response_language: params.response_language ?? "ko",
    }),
  })
}

export async function fetchApprovals(): Promise<ApprovalItem[]> {
  return request<ApprovalItem[]>("/approvals")
}

export async function approveAction(actionId: string): Promise<{
  action_id: string
  session_id: string
  result: string
  status: string
}> {
  return request(`/approvals/${actionId}/approve`, {
    method: "POST",
  })
}

export async function rejectAction(actionId: string): Promise<{
  action_id: string
  session_id: string
  result: string
  status: string
}> {
  return request(`/approvals/${actionId}/reject`, {
    method: "POST",
  })
}

export async function fetchMemories(limit = 10): Promise<MemoryItem[]> {
  return request<MemoryItem[]>(`/memories?limit=${limit}`)
}

export async function fetchSessionHistory(sessionId: string): Promise<ChatMessage[]> {
  return request<ChatMessage[]>(`/sessions/${sessionId}/history`)
}

export async function renameSession(sessionId: string, title: string): Promise<{
  session_id: string
  title: string
}> {
  return request(`/sessions/${sessionId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  })
}

export async function deleteSession(sessionId: string): Promise<{
  deleted: boolean
  session_id: string
}> {
  return request(`/sessions/${sessionId}`, {
    method: "DELETE",
  })
}

export async function createMemory(params: {
  content: string
  tags?: string[]
  importance?: number
  note_type?: string
  source_session_id?: string | null
}): Promise<{
  memory_id: string
  timestamp: string
  content: string
  tags: string[]
  importance: number
  note_type: string
  source_session_id?: string | null
}> {
  return request("/memories", {
    method: "POST",
    body: JSON.stringify({
      content: params.content,
      tags: params.tags ?? [],
      importance: params.importance ?? 3,
      note_type: params.note_type ?? "general",
      source_session_id: params.source_session_id ?? null,
    }),
  })
}

export async function updateMemory(params: {
  memoryId: string
  new_content: string
  new_tags?: string[] | null
  new_importance?: number | null
  new_note_type?: string | null
}): Promise<{
  memory_id: string
  timestamp: string
  content: string
  tags: string[]
  importance: number
  note_type: string
}> {
  return request(`/memories/${params.memoryId}`, {
    method: "PATCH",
    body: JSON.stringify({
      new_content: params.new_content,
      new_tags: params.new_tags ?? null,
      new_importance: params.new_importance ?? null,
      new_note_type: params.new_note_type ?? null,
    }),
  })
}

export async function deleteMemory(memoryId: string): Promise<{
  deleted: boolean
  memory_id: string
}> {
  return request(`/memories/${memoryId}`, {
    method: "DELETE",
  })
}

export async function fetchMemorySuggestions(): Promise<MemorySuggestionItem[]> {
  return request<MemorySuggestionItem[]>("/memory-suggestions")
}

export async function saveMemorySuggestion(choice: string): Promise<{
  memory_id: string
  timestamp: string
  content: string
  tags: string[]
  importance: number
  note_type: string
}> {
  return request(`/memory-suggestions/${choice}/save`, {
    method: "POST",
  })
}

export async function dropMemorySuggestion(choice: string): Promise<{
  dismissed: boolean
  suggestion_id: string
  content: string
}> {
  return request(`/memory-suggestions/${choice}/drop`, {
    method: "POST",
  })
}

export async function fetchSessionToolLogs(
  sessionId: string,
  limit = 50,
): Promise<ToolLogItem[]> {
  return request<ToolLogItem[]>(`/sessions/${sessionId}/tool-logs?limit=${limit}`)
}

export async function fetchSessionToolPanel(
  sessionId: string,
): Promise<ToolPanelData> {
  return request<ToolPanelData>(`/sessions/${sessionId}/tool-panel`)
}