import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import "./index.css"
import {
  approveAction,
  createMemory,
  createSession,
  deleteMemory,
  deleteSession,
  dropMemorySuggestion,
  fetchApprovals,
  fetchMemories,
  fetchMemorySuggestions,
  fetchSessionHistory,
  fetchSessionWorkspaceState,
  fetchSessions,
  rejectAction,
  renameSession,
  saveMemorySuggestion,
  sendChat,
  updateMemory,
  fetchSessionToolLogs,
  fetchSessionToolPanel,
} from "./api"
import type {
  ApprovalItem,
  ChatMessage,
  MemoryItem,
  MemorySuggestionItem,
  SessionItem,
  WorkspaceState,
  ToolLogItem,
  ToolPanelData,
} from "./types"

type CollapsibleSectionProps = {
  title: string
  isOpen: boolean
  onToggle: () => void
  actions?: ReactNode
  children: ReactNode
}

function CollapsibleSection({
  title,
  isOpen,
  onToggle,
  actions,
  children,
}: CollapsibleSectionProps) {
  return (
    <section className="collapsible-section">
      <div className="collapsible-header">
        <button
          type="button"
          className="collapsible-toggle"
          onClick={onToggle}
        >
          <span>{title}</span>
          <span className="collapsible-chevron">{isOpen ? "▾" : "▸"}</span>
        </button>

        {actions ? (
          <div
            className="collapsible-actions"
            onClick={(e) => e.stopPropagation()}
          >
            {actions}
          </div>
        ) : null}
      </div>

      {isOpen ? <div className="collapsible-body">{children}</div> : null}
    </section>
  )
}

export default function App() {
  const [sessions, setSessions] = useState<SessionItem[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)

  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")

  const [approvals, setApprovals] = useState<ApprovalItem[]>([])
  const [memories, setMemories] = useState<MemoryItem[]>([])

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [memoryContentInput, setMemoryContentInput] = useState("")
  const [memoryTagsInput, setMemoryTagsInput] = useState("")
  const [memoryImportanceInput, setMemoryImportanceInput] = useState(3)
  const [memoryTypeInput, setMemoryTypeInput] = useState("general")
  const [memorySuggestions, setMemorySuggestions] = useState<MemorySuggestionItem[]>([])

  const [sessionTitleInput, setSessionTitleInput] = useState("")

  const [workspaceState, setWorkspaceState] = useState<WorkspaceState | null>(null)

  const [toolLogs, setToolLogs] = useState<ToolLogItem[]>([])
  const [toolPanel, setToolPanel] = useState<ToolPanelData | null>(null)

  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true)
  const [rightSidebarOpen, setRightSidebarOpen] = useState(true)

  const [sectionOpen, setSectionOpen] = useState({
    currentSession: true,
    sessionList: true,
    approvals: true,
    workspace: true,
    resources: true,
    suggestions: true,
    memories: true,
    toolLogs: true,
  })

  const messagesEndRef = useRef<HTMLDivElement | null>(null)
  const previousMessageCountRef = useRef(0)

  const [isSyncing, setIsSyncing] = useState(false)
  
  function toggleSection(key: keyof typeof sectionOpen) {
    setSectionOpen((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  const shellClassName = [
    "app-shell",
    !leftSidebarOpen ? "left-sidebar-closed" : "",
    !rightSidebarOpen ? "right-sidebar-closed" : "",
  ]
    .filter(Boolean)
    .join(" ")

  useEffect(() => {
    if (messages.length === 0) {
      previousMessageCountRef.current = 0
      return
    }

    const isNewMessage = messages.length > previousMessageCountRef.current
    const lastMessage = messages[messages.length - 1]

    if (isNewMessage && lastMessage.role === "assistant") {
      requestAnimationFrame(() => {
        messagesEndRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "end",
        })
      })
    }

    previousMessageCountRef.current = messages.length
  }, [messages])

  function getApprovalLabel(item: ApprovalItem): string {
    switch (item.action_type) {
      case "create_file":
        return "빈 파일 생성"
      case "write_file":
        return "내용 포함 파일 생성"
      case "replace_text_in_file":
        return "파일 내용 수정"
      case "delete_path":
        return "파일/폴더 삭제"
      case "search_files":
        return "파일 검색"
      case "batch_operations":
        return "배치 작업"
      default:
        return item.action_type
    }
  }

  function extractPathFromSummary(summary: string): string | null {
    const match = summary.match(/path='([^']+)'/)
    return match ? match[1] : null
  }

  function extractContentLengthFromSummary(summary: string): number | null {
    const match = summary.match(/content_length=(\d+)/)
    return match ? Number(match[1]) : null
  }

  function extractOperationCount(item: ApprovalItem): number | null {
    const operations = item.payload?.operations
    return Array.isArray(operations) ? operations.length : null
  }

  async function handleSaveSuggestion(suggestionId: string) {
    try {
      setError(null)
      await saveMemorySuggestion(suggestionId)
      await Promise.all([refreshMemories(), refreshMemorySuggestions()])
    } catch (err) {
      setError(err instanceof Error ? err.message : "기억 후보 저장 실패")
    }
  }

  async function handleDropSuggestion(suggestionId: string) {
    try {
      setError(null)
      await dropMemorySuggestion(suggestionId)
      await refreshMemorySuggestions()
    } catch (err) {
      setError(err instanceof Error ? err.message : "기억 후보 폐기 실패")
    }
  }

  async function handleRenameCurrentSession() {
    if (!currentSessionId) {
      setError("선택된 세션이 없습니다.")
      return
    }

    const title = sessionTitleInput.trim()
    if (!title) {
      setError("세션 이름은 비어 있을 수 없습니다.")
      return
    }

    try {
      setError(null)
      await renameSession(currentSessionId, title)
      await refreshSessions()
    } catch (err) {
      setError(err instanceof Error ? err.message : "세션 이름 변경 실패")
    }
  }

  async function handleDeleteCurrentSession() {
    if (!currentSessionId) {
      setError("선택된 세션이 없습니다.")
      return
    }

    const ok = window.confirm("현재 세션을 삭제할까요?")
    if (!ok) return

    try {
      setError(null)
      await deleteSession(currentSessionId)

      const sessionData = await fetchSessions()
      setSessions(sessionData)

      if (sessionData.length > 0) {
        const nextSessionId = sessionData[0].session_id
        setCurrentSessionId(nextSessionId)
        const history = await fetchSessionHistory(nextSessionId)
        setMessages(history)
      } else {
        setCurrentSessionId(null)
        setMessages([])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "세션 삭제 실패")
    }
  }

  async function handleCreateMemory() {
    const content = memoryContentInput.trim()
    if (!content) {
      setError("기억 내용이 비어 있습니다.")
      return
    }

    try {
      setError(null)

      const tags = memoryTagsInput
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)

      await createMemory({
        content,
        tags,
        importance: memoryImportanceInput,
        note_type: memoryTypeInput,
        source_session_id: currentSessionId,
      })

      setMemoryContentInput("")
      setMemoryTagsInput("")
      setMemoryImportanceInput(3)
      setMemoryTypeInput("general")

      await refreshMemories()
    } catch (err) {
      setError(err instanceof Error ? err.message : "장기 기억 생성 실패")
    }
  }

  async function handleUpdateMemory(memory: MemoryItem) {
    const nextContent = window.prompt("새 기억 내용을 입력하세요.", memory.content)
    if (nextContent === null) return

    const trimmed = nextContent.trim()
    if (!trimmed) {
      setError("기억 내용은 비어 있을 수 없습니다.")
      return
    }

    try {
      setError(null)
      await updateMemory({
        memoryId: memory.memory_id,
        new_content: trimmed,
        new_tags: memory.tags,
        new_importance: memory.importance,
        new_note_type: memory.note_type,
      })
      await refreshMemories()
    } catch (err) {
      setError(err instanceof Error ? err.message : "장기 기억 수정 실패")
    }
  }

  async function handleDeleteMemory(memoryId: string) {
    const ok = window.confirm("이 장기 기억을 삭제할까요?")
    if (!ok) return

    try {
      setError(null)
      await deleteMemory(memoryId)
      await refreshMemories()
    } catch (err) {
      setError(err instanceof Error ? err.message : "장기 기억 삭제 실패")
    }
  }

  async function refreshSessions() {
    const data = await fetchSessions()
    setSessions(data)
  }

  async function refreshApprovals() {
    const data = await fetchApprovals()
    setApprovals(data)
  }

  async function refreshMemories() {
    const data = await fetchMemories(10)
    setMemories(data)
  }

  async function refreshMemorySuggestions() {
    const data = await fetchMemorySuggestions()
    setMemorySuggestions(data)
  }

  async function refreshWorkspaceState(sessionId: string | null) {
    if (!sessionId) {
      setWorkspaceState(null)
      return
    }

    const data = await fetchSessionWorkspaceState(sessionId)
    setWorkspaceState(data)
  }

  async function refreshToolLogs(sessionId: string | null) {
    if (!sessionId) {
      setToolLogs([])
      return
    }

    const data = await fetchSessionToolLogs(sessionId, 50)
    setToolLogs(data)
  }

  async function refreshToolPanel(sessionId: string | null) {
    if (!sessionId) {
      setToolPanel(null)
      return
    }

    const data = await fetchSessionToolPanel(sessionId)
    setToolPanel(data)
  }

  async function refreshRightSidebar(sessionId: string | null) {
    await Promise.all([
      refreshApprovals(),
      refreshMemories(),
      refreshMemorySuggestions(),
      refreshWorkspaceState(sessionId),
      refreshToolLogs(sessionId),
      refreshToolPanel(sessionId),
    ])
  }

  async function refreshSessionView(sessionId: string | null) {
    if (!sessionId) {
      setMessages([])
      setWorkspaceState(null)
      setToolLogs([])
      setToolPanel(null)

      await Promise.all([
        refreshSessions(),
        refreshApprovals(),
        refreshMemories(),
        refreshMemorySuggestions(),
      ])
      return
    }

    const [history] = await Promise.all([
      fetchSessionHistory(sessionId),
      refreshSessions(),
      refreshRightSidebar(sessionId),
    ])

    setMessages(history)
  }

  async function handleManualSync() {
    try {
      setError(null)
      setIsSyncing(true)
      await refreshSessionView(currentSessionId)
    } catch (err) {
      setError(err instanceof Error ? err.message : "동기화 실패")
    } finally {
      setIsSyncing(false)
    }
  }

  async function bootstrap() {
    try {
      setError(null)

      const [sessionData, approvalData, memoryData, suggestionData] = await Promise.all([
        fetchSessions(),
        fetchApprovals(),
        fetchMemories(10),
        fetchMemorySuggestions(),
      ])

      setSessions(sessionData)
      setApprovals(approvalData)
      setMemories(memoryData)
      setMemorySuggestions(suggestionData)

      // 처음 접속 시에는 자동으로 기존 세션 히스토리를 로드하지 않음
      setCurrentSessionId(null)
      setMessages([])
      setWorkspaceState(null)
      setToolLogs([])
      setToolPanel(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "초기 로딩 실패")
    }
  }

  useEffect(() => {
    bootstrap()
  }, [])

  useEffect(() => {
    if (!currentSessionId) return
    if (!loading && approvals.length === 0) return

    const timer = window.setInterval(() => {
      refreshRightSidebar(currentSessionId).catch(() => {
        // polling 실패는 조용히 무시
      })
    }, 4000)

    return () => window.clearInterval(timer)
  }, [currentSessionId, loading, approvals.length])

  async function handleCreateSession() {
    try {
      setError(null)
      const created = await createSession()
      await refreshSessions()
      setCurrentSessionId(created.session_id)
      setMessages([])
      setWorkspaceState(null)
      setToolLogs([])
      setToolPanel(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "세션 생성 실패")
    }
  }

  async function handleSelectSession(sessionId: string) {
    try {
      setError(null)
      setCurrentSessionId(sessionId)
      await refreshSessionView(sessionId)
    } catch (err) {
      setError(err instanceof Error ? err.message : "세션 히스토리 로딩 실패")
    }
  }

   async function handleSend() {
     const trimmed = input.trim()
     if (!trimmed || loading) return
 
     const userMessage: ChatMessage = {
       role: "user",
       content: trimmed,
     }
 
     setMessages((prev) => [...prev, userMessage])
     setInput("")
     setLoading(true)
     setError(null)
 
     try {
       const result = await sendChat({
         message: trimmed,
         session_id: currentSessionId,
         output_mode: "markdown",
         response_language: "ko",
       })
 
       setCurrentSessionId(result.session_id)
 
       setMessages((prev) => [
         ...prev,
         {
           role: "assistant",
           content: result.answer,
         },
       ])
 
       // 히스토리는 로컬에 이미 추가되었으므로, 사이드바 정보만 업데이트
       if (result.action_id && result.action_required) {
         // 승인 요청: 즉시 로컬 approvals에 추가하고 모달 표시
         const newApproval: ApprovalItem = {
           action_id: result.action_id,
           action_type: "batch_operations",
           summary: result.action_summary || "승인 대기 작업",
           status: "pending",
           payload: {},
           created_at: new Date().toISOString(),
         }
         setApprovals((prev) => [newApproval, ...prev])
         setSelectedApprovalId(result.action_id)
         setApprovalModalOpen(true)
         
         // 백그라운드에서 전체 승인 목록 동기화
         refreshApprovals().catch(() => {})
       } else {
         // 일반 응답: 전체 세션 뷰 새로고침 (히스토리 + 사이드바)
         await refreshSessionView(result.session_id)
       }
     } catch (err) {
       setError(err instanceof Error ? err.message : "채팅 요청 실패")
     } finally {
       setLoading(false)
     }
   }

  async function handleApprove(actionId: string) {
    try {
      setError(null)
      const result = await approveAction(actionId)

      if (result.session_id) {
        setCurrentSessionId(result.session_id)
        await refreshSessionView(result.session_id)
      } else {
        await refreshRightSidebar(currentSessionId)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "승인 처리 실패")
    }
  }

  async function handleReject(actionId: string) {
    try {
      setError(null)
      const result = await rejectAction(actionId)

      if (result.session_id) {
        setCurrentSessionId(result.session_id)
        await refreshSessionView(result.session_id)
      } else {
        await refreshRightSidebar(currentSessionId)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "거부 처리 실패")
    }
  }

  const currentSessionTitle = useMemo(() => {
    const found = sessions.find((item) => item.session_id === currentSessionId)
    return found?.title ?? "(선택된 세션 없음)"
  }, [sessions, currentSessionId])

  useEffect(() => {
    const found = sessions.find((item) => item.session_id === currentSessionId)
    setSessionTitleInput(found?.title ?? "")
  }, [sessions, currentSessionId])

  return (
   <>
    <button
    type="button"
    className={`edge-toggle left ${leftSidebarOpen ? "open" : "closed"}`}
    onClick={() => setLeftSidebarOpen((prev) => !prev)}
    aria-label={leftSidebarOpen ? "왼쪽 패널 닫기" : "왼쪽 패널 열기"}
    title={leftSidebarOpen ? "왼쪽 패널 닫기" : "왼쪽 패널 열기"}
    >
    {leftSidebarOpen ? "◂" : "▸"}
    </button>

    <button
    type="button"
    className={`edge-toggle right ${rightSidebarOpen ? "open" : "closed"}`}
    onClick={() => setRightSidebarOpen((prev) => !prev)}
    aria-label={rightSidebarOpen ? "오른쪽 패널 닫기" : "오른쪽 패널 열기"}
    title={rightSidebarOpen ? "오른쪽 패널 닫기" : "오른쪽 패널 열기"}
    >
    {rightSidebarOpen ? "▸" : "◂"}
    </button>

  
    <div className={shellClassName}>
      {leftSidebarOpen ? (
        <aside className="panel side-panel left-panel">
          <div className="sidebar-scroll">
            <CollapsibleSection
              title="현재 세션"
              isOpen={sectionOpen.currentSession}
              onToggle={() => toggleSection("currentSession")}
            >
              <div className="session-current">
                <div className="label">현재 세션</div>
                <div className="value">{currentSessionTitle}</div>
                <div className="subvalue">{currentSessionId ?? "-"}</div>

                <div className="session-edit-box">
                  <input
                    value={sessionTitleInput}
                    onChange={(e) => setSessionTitleInput(e.target.value)}
                    placeholder="세션 이름"
                  />
                  <div className="inline-actions">
                    <button onClick={handleRenameCurrentSession}>
                      이름 변경
                    </button>
                    <button
                      className="danger"
                      onClick={handleDeleteCurrentSession}
                    >
                      삭제
                    </button>
                  </div>
                </div>
              </div>
            </CollapsibleSection>

            <CollapsibleSection
              title="세션 목록"
              isOpen={sectionOpen.sessionList}
              onToggle={() => toggleSection("sessionList")}
              actions={<button onClick={handleCreateSession}>새 세션</button>}
            >
              <div className="session-list">
                {sessions.map((session) => (
                  <button
                    key={session.session_id}
                    className={
                      session.session_id === currentSessionId
                        ? "session-item active"
                        : "session-item"
                    }
                    onClick={() => {
                      handleSelectSession(session.session_id)
                    }}
                  >
                    <div className="title">
                      {session.title ?? "(untitled)"}
                    </div>
                    <div className="meta">{session.session_id}</div>
                  </button>
                ))}
              </div>
            </CollapsibleSection>
          </div>
        </aside>
      ) : null}

      <main className="panel chat-panel">
        <div className="panel-header">
          <h2>채팅</h2>
        </div>

        {error && <div className="error-box">{error}</div>}

        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty-box">
              메시지가 없습니다. 질문을 보내면 여기 표시됩니다.
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={
                  message.role === "user" ? "message user-message" : "message assistant-message"
                }
              >
                <div className="message-role">
                  {message.role === "user" ? "사용자" : "에이전트"}
                </div>
                {message.role === "assistant" ? (
                  <div className="message-content markdown-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <pre className="message-content">{message.content}</pre>
                )}
              </div>
            ))
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="tool-log-section">
            <CollapsibleSection
                title="툴 실행 로그"
                isOpen={sectionOpen.toolLogs}
                onToggle={() => toggleSection("toolLogs")}
            >
                {!currentSessionId ? (
                    <div className="empty-box">선택된 세션이 없습니다.</div>
                ) : toolLogs.length === 0 ? (
                    <div className="empty-box">기록된 툴 실행 로그가 없습니다.</div>
                ) : (
                    <div className="tool-log-list">
                        {toolLogs
                            .slice()
                            .reverse()
                            .map((log, index) => (
                                <div key={`${log.timestamp}-${index}`} className="tool-log-card">
                                    <div className="tool-log-top">
                                        <span>{log.tool_name}</span>
                                        <span>step {log.step_index}</span>
                                    </div>

                                    <div className="tool-log-meta">{log.timestamp}</div>

                                    <div className="tool-log-block">
                                        <div className="tool-log-label">arguments</div>
                                        <pre className="tool-log-pre">
                                            {JSON.stringify(log.arguments, null, 2)}
                                        </pre>
                                    </div>

                                    <div className="tool-log-block">
                                        <div className="tool-log-label">result preview</div>
                                        <pre className="tool-log-pre">{log.result_preview}</pre>
                                    </div>
                                </div>
                            ))}
                    </div>
                )}
            </CollapsibleSection>
        </div>

        <div className="composer">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="메시지를 입력하세요"
            rows={5}
          />
          <button onClick={handleSend} disabled={loading}>
            {loading ? "전송 중..." : "보내기"}
          </button>
        </div>
      </main>

      {rightSidebarOpen ? (
        <aside className="panel side-panel right-panel">
          <div className="inline-actions" style={{ marginBottom: 10 }}>
            <button onClick={handleManualSync} disabled={isSyncing}>
              {isSyncing ? "동기화 중..." : "동기화"}
            </button>
          </div>

          <div className="sidebar-scroll">
            <CollapsibleSection
              title="승인 대기"
              isOpen={sectionOpen.approvals}
              onToggle={() => toggleSection("approvals")}
            >
              {approvals.length === 0 ? (
                <div className="empty-box">대기 중인 승인 요청이 없습니다.</div>
              ) : (
                approvals.map((item) => {
                  const path = extractPathFromSummary(item.summary)
                  const contentLength = extractContentLengthFromSummary(item.summary)
                  const operationCount = extractOperationCount(item)

                  return (
                    <div key={item.action_id} className="approval-card">
                      <div className="approval-top">
                        <span className="approval-kind">{getApprovalLabel(item)}</span>
                        <span className="approval-id">{item.action_id}</span>
                      </div>

                      {path && <div className="approval-path">path: {path}</div>}

                      {item.action_type === "write_file" && contentLength !== null && (
                        <div className="approval-meta-line">
                          content_length: {contentLength}
                        </div>
                      )}

                      {item.action_type === "batch_operations" && operationCount !== null && (
                        <div className="approval-meta-line">
                          operations: {operationCount}
                        </div>
                      )}

                      <div className="approval-summary">{item.summary}</div>

                      <div className="approval-actions">
                        <button onClick={() => handleApprove(item.action_id)}>승인</button>
                        <button
                          className="danger"
                          onClick={() => handleReject(item.action_id)}
                        >
                          거부
                        </button>
                      </div>
                    </div>
                  )
                })
              )}
            </CollapsibleSection>

            <CollapsibleSection
              title="작업 상태"
              isOpen={sectionOpen.workspace}
              onToggle={() => toggleSection("workspace")}
            >
              {!currentSessionId ? (
                <div className="empty-box">선택된 세션이 없습니다.</div>
              ) : !workspaceState || Object.keys(workspaceState).length === 0 ? (
                <div className="empty-box">기록된 작업 상태가 없습니다.</div>
              ) : (
                <div className="workspace-card">
                  {workspaceState.last_created_path && (
                    <div className="workspace-row">
                      <span className="workspace-label">마지막 생성</span>
                      <span className="workspace-value">
                        {workspaceState.last_created_path}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_written_path && (
                    <div className="workspace-row">
                      <span className="workspace-label">마지막 쓰기</span>
                      <span className="workspace-value">
                        {workspaceState.last_written_path}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_modified_path && (
                    <div className="workspace-row">
                      <span className="workspace-label">마지막 수정</span>
                      <span className="workspace-value">
                        {workspaceState.last_modified_path}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_deleted_path && (
                    <div className="workspace-row">
                      <span className="workspace-label">마지막 삭제</span>
                      <span className="workspace-value">
                        {workspaceState.last_deleted_path}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_read_path && (
                    <div className="workspace-row">
                      <span className="workspace-label">마지막 읽기</span>
                      <span className="workspace-value">
                        {workspaceState.last_read_path}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_search_query && (
                    <div className="workspace-row">
                      <span className="workspace-label">마지막 검색어</span>
                      <span className="workspace-value">
                        {workspaceState.last_search_query}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_search_path && (
                    <div className="workspace-row">
                      <span className="workspace-label">검색 경로</span>
                      <span className="workspace-value">
                        {workspaceState.last_search_path}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_action_type && (
                    <div className="workspace-row">
                      <span className="workspace-label">마지막 액션</span>
                      <span className="workspace-value">
                        {workspaceState.last_action_type}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_action_status && (
                    <div className="workspace-row">
                      <span className="workspace-label">액션 상태</span>
                      <span className="workspace-value">
                        {workspaceState.last_action_status}
                      </span>
                    </div>
                  )}

                  {workspaceState.last_pending_summary && (
                    <div className="workspace-row">
                      <span className="workspace-label">대기 중 요청</span>
                      <span className="workspace-value">
                        {workspaceState.last_pending_summary}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </CollapsibleSection>

            <CollapsibleSection
              title="노트 / 파일 결과"
              isOpen={sectionOpen.resources}
              onToggle={() => toggleSection("resources")}
            >
              {!currentSessionId ? (
                <div className="empty-box">선택된 세션이 없습니다.</div>
              ) : !toolPanel ? (
                <div className="empty-box">표시할 결과가 없습니다.</div>
              ) : (
                <div className="resource-panel">
                  {toolPanel.last_note_search && (
                    <div className="resource-card">
                      <div className="resource-title">마지막 노트 검색</div>
                      {toolPanel.last_note_search.query && (
                        <div className="resource-meta">
                          query: {toolPanel.last_note_search.query}
                        </div>
                      )}

                      {toolPanel.last_note_search.items.length === 0 ? (
                        <div className="resource-empty">검색 결과 없음</div>
                      ) : (
                        toolPanel.last_note_search.items.map((item, index) => (
                          <div
                            key={`${item.path ?? "item"}-${index}`}
                            className="resource-item"
                          >
                            {item.path && (
                              <div className="resource-path">{item.path}</div>
                            )}
                            {item.score && (
                              <div className="resource-meta">score: {item.score}</div>
                            )}
                            {item.preview && (
                              <div className="resource-preview">{item.preview}</div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {toolPanel.last_note_read && (
                    <div className="resource-card">
                      <div className="resource-title">마지막 노트 읽기</div>
                      {toolPanel.last_note_read.path && (
                        <div className="resource-path">
                          {toolPanel.last_note_read.path}
                        </div>
                      )}
                      <div className="resource-preview">
                        {toolPanel.last_note_read.content_preview}
                      </div>
                    </div>
                  )}

                  {toolPanel.last_file_read && (
                    <div className="resource-card">
                      <div className="resource-title">마지막 파일 읽기</div>
                      {toolPanel.last_file_read.path && (
                        <div className="resource-path">
                          {toolPanel.last_file_read.path}
                        </div>
                      )}
                      <div className="resource-preview">
                        {toolPanel.last_file_read.content_preview}
                      </div>
                    </div>
                  )}

                  {!toolPanel.last_note_search &&
                    !toolPanel.last_note_read &&
                    !toolPanel.last_file_read && (
                      <div className="empty-box">최근 노트/파일 결과가 없습니다.</div>
                    )}
                </div>
              )}
            </CollapsibleSection>

            <CollapsibleSection
              title="기억 후보"
              isOpen={sectionOpen.suggestions}
              onToggle={() => toggleSection("suggestions")}
            >
              {memorySuggestions.length === 0 ? (
                <div className="empty-box">저장 제안된 장기 기억이 없습니다.</div>
              ) : (
                memorySuggestions.map((item) => (
                  <div key={item.suggestion_id} className="suggestion-card">
                    <div className="suggestion-top">
                      <span>{item.suggestion_id}</span>
                      <span>{item.note_type}</span>
                    </div>

                    <div className="suggestion-content">{item.content}</div>

                    <div className="memory-meta">
                      importance: {item.importance} | tags:{" "}
                      {item.tags.length ? item.tags.join(", ") : "-"}
                    </div>

                    <div className="inline-actions">
                      <button onClick={() => handleSaveSuggestion(item.suggestion_id)}>
                        저장
                      </button>
                      <button
                        className="danger"
                        onClick={() => handleDropSuggestion(item.suggestion_id)}
                      >
                        폐기
                      </button>
                    </div>
                  </div>
                ))
              )}
            </CollapsibleSection>

            <CollapsibleSection
              title="장기 기억"
              isOpen={sectionOpen.memories}
              onToggle={() => toggleSection("memories")}
            >
              <div className="memory-create-box">
                <textarea
                  value={memoryContentInput}
                  onChange={(e) => setMemoryContentInput(e.target.value)}
                  placeholder="새 장기 기억 내용을 입력하세요"
                  rows={4}
                />
                <input
                  value={memoryTagsInput}
                  onChange={(e) => setMemoryTagsInput(e.target.value)}
                  placeholder="태그 (쉼표로 구분)"
                />
                <div className="memory-create-row">
                  <label>
                    중요도
                    <input
                      type="number"
                      min={1}
                      max={5}
                      value={memoryImportanceInput}
                      onChange={(e) => setMemoryImportanceInput(Number(e.target.value))}
                    />
                  </label>
                  <label>
                    타입
                    <input
                      value={memoryTypeInput}
                      onChange={(e) => setMemoryTypeInput(e.target.value)}
                    />
                  </label>
                </div>
                <button onClick={handleCreateMemory}>장기 기억 추가</button>
              </div>

              {memories.length === 0 ? (
                <div className="empty-box">장기 기억이 없습니다.</div>
              ) : (
                memories.map((memory) => (
                  <div key={memory.memory_id} className="memory-card">
                    <div className="memory-top">
                      <span>{memory.memory_id}</span>
                      <span>{memory.note_type}</span>
                    </div>
                    <div className="memory-content">{memory.content}</div>
                    <div className="memory-meta">
                      importance: {memory.importance} | tags:{" "}
                      {memory.tags.length ? memory.tags.join(", ") : "-"}
                    </div>
                    <div className="inline-actions">
                      <button onClick={() => handleUpdateMemory(memory)}>수정</button>
                      <button
                        className="danger"
                        onClick={() => handleDeleteMemory(memory.memory_id)}
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                ))
              )}
            </CollapsibleSection>
          </div>
        </aside>
      ) : null}
    </div>
   </>
  )

}