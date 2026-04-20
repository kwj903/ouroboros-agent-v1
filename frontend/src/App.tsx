import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from "react"
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
  ToolLogItem,
  ToolPanelData,
  WorkspaceState,
} from "./types"
import { ChatPanel } from "./components/ChatPanel"
import { OperationsSidebar } from "./components/OperationsSidebar"
import { SessionSidebar } from "./components/SessionSidebar"

type SectionState = {
  currentSession: boolean
  sessionList: boolean
  approvals: boolean
  workspace: boolean
  resources: boolean
  suggestions: boolean
  memories: boolean
  toolLogs: boolean
}

type SessionSnapshot = {
  messages: ChatMessage[]
  workspaceState: WorkspaceState
  toolLogs: ToolLogItem[]
  toolPanel: ToolPanelData
}

type ExecutionStateSnapshot = {
  approvals: ApprovalItem[]
  workspaceState: WorkspaceState | null
  toolLogs: ToolLogItem[]
  toolPanel: ToolPanelData | null
}

function isStaleSuggestionError(err: unknown): boolean {
  return (
    err instanceof Error &&
    err.message.includes("API 404") &&
    err.message.includes("suggestion not found")
  )
}

const INITIAL_SECTION_STATE: SectionState = {
  currentSession: true,
  sessionList: true,
  approvals: true,
  workspace: true,
  resources: true,
  suggestions: true,
  memories: true,
  toolLogs: true,
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
  const [sectionOpen, setSectionOpen] = useState(INITIAL_SECTION_STATE)
  const [isSyncing, setIsSyncing] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement | null>(null)
  const previousMessageCountRef = useRef(0)
  const activeSessionRequestRef = useRef<string | null>(null)

  function toggleSection(key: keyof SectionState) {
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

  async function handleSaveSuggestion(suggestionId: string) {
    try {
      setError(null)
      await saveMemorySuggestion(suggestionId)
      await Promise.all([refreshMemories(), refreshMemorySuggestions()])
    } catch (err) {
      if (isStaleSuggestionError(err)) {
        await refreshMemorySuggestions().catch(() => undefined)
        setError("이미 처리되었거나 비활성화된 후보입니다.")
        return
      }

      setError(err instanceof Error ? err.message : "기억 후보 저장 실패")
    }
  }

  async function handleDropSuggestion(suggestionId: string) {
    try {
      setError(null)
      await dropMemorySuggestion(suggestionId)
      await refreshMemorySuggestions()
    } catch (err) {
      if (isStaleSuggestionError(err)) {
        await refreshMemorySuggestions().catch(() => undefined)
        setError("이미 처리되었거나 비활성화된 후보입니다.")
        return
      }

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
        await refreshSessionView(nextSessionId)
      } else {
        setCurrentSessionId(null)
        await refreshSessionView(null)
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

  async function refreshMemories() {
    const data = await fetchMemories(10)
    setMemories(data)
  }

  async function refreshMemorySuggestions() {
    const data = await fetchMemorySuggestions()
    setMemorySuggestions(data)
  }

  async function loadSessionSnapshot(
    sessionId: string,
  ): Promise<SessionSnapshot> {
    const [nextMessages, nextWorkspaceState, nextToolLogs, nextToolPanel] =
      await Promise.all([
        fetchSessionHistory(sessionId),
        fetchSessionWorkspaceState(sessionId),
        fetchSessionToolLogs(sessionId, 50),
        fetchSessionToolPanel(sessionId),
      ])

    return {
      messages: nextMessages,
      workspaceState: nextWorkspaceState,
      toolLogs: nextToolLogs,
      toolPanel: nextToolPanel,
    }
  }

  function applySessionSnapshot(
    sessionId: string,
    snapshot: SessionSnapshot,
  ) {
    if (activeSessionRequestRef.current !== sessionId) {
      return
    }

    setMessages(snapshot.messages)
    setWorkspaceState(snapshot.workspaceState)
    setToolLogs(snapshot.toolLogs)
    setToolPanel(snapshot.toolPanel)
  }

  function clearSessionSnapshot() {
    setMessages([])
    setWorkspaceState(null)
    setToolLogs([])
    setToolPanel(null)
  }

  function applyExecutionState(
    sessionId: string | null,
    snapshot: ExecutionStateSnapshot,
  ) {
    setApprovals(snapshot.approvals)

    if (activeSessionRequestRef.current !== sessionId) {
      return
    }

    setWorkspaceState(snapshot.workspaceState)
    setToolLogs(snapshot.toolLogs)
    setToolPanel(snapshot.toolPanel)
  }

  async function refreshExecutionState(
    sessionId: string | null,
    snapshot?: SessionSnapshot,
  ) {
    const [nextApprovals, nextWorkspaceState, nextToolLogs, nextToolPanel] =
      await Promise.all([
        fetchApprovals(),
        snapshot
          ? Promise.resolve(snapshot.workspaceState)
          : sessionId
            ? fetchSessionWorkspaceState(sessionId)
            : Promise.resolve(null),
        snapshot
          ? Promise.resolve(snapshot.toolLogs)
          : sessionId
            ? fetchSessionToolLogs(sessionId, 50)
            : Promise.resolve([]),
        snapshot
          ? Promise.resolve(snapshot.toolPanel)
          : sessionId
            ? fetchSessionToolPanel(sessionId)
            : Promise.resolve(null),
      ])

    applyExecutionState(sessionId, {
      approvals: nextApprovals,
      workspaceState: nextWorkspaceState,
      toolLogs: nextToolLogs,
      toolPanel: nextToolPanel,
    })
  }

  async function refreshGlobalSidebarState() {
    await Promise.all([refreshMemories(), refreshMemorySuggestions()])
  }

  async function refreshSessionView(sessionId: string | null) {
    activeSessionRequestRef.current = sessionId

    if (!sessionId) {
      clearSessionSnapshot()

      await Promise.all([
        refreshSessions(),
        refreshExecutionState(null),
        refreshGlobalSidebarState(),
      ])
      return
    }

    const [snapshot] = await Promise.all([
      loadSessionSnapshot(sessionId),
      refreshSessions(),
      refreshGlobalSidebarState(),
    ])

    applySessionSnapshot(sessionId, snapshot)
    await refreshExecutionState(sessionId, snapshot)
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

      if (sessionData.length === 0) {
        activeSessionRequestRef.current = null
        setCurrentSessionId(null)
        clearSessionSnapshot()
        return
      }

      const nextSessionId = sessionData[0].session_id
      activeSessionRequestRef.current = nextSessionId
      setCurrentSessionId(nextSessionId)

      const snapshot = await loadSessionSnapshot(nextSessionId)
      applySessionSnapshot(nextSessionId, snapshot)
    } catch (err) {
      setError(err instanceof Error ? err.message : "초기 로딩 실패")
    }
  }

  useEffect(() => {
    void bootstrap()
  }, [])

  useEffect(() => {
    if (!currentSessionId) return
    if (!loading && approvals.length === 0) return

    const timer = window.setInterval(() => {
      refreshExecutionState(currentSessionId).catch(() => {
        // polling 실패는 조용히 무시
      })
    }, 4000)

    return () => window.clearInterval(timer)
  }, [currentSessionId, loading, approvals.length])

  async function handleCreateSession() {
    try {
      setError(null)
      const created = await createSession()
      setCurrentSessionId(created.session_id)
      await refreshSessionView(created.session_id)
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

    const previousMessages = messages
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
      await refreshSessionView(result.session_id)
    } catch (err) {
      setMessages(previousMessages)
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
        await refreshExecutionState(currentSessionId)
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
        await refreshExecutionState(currentSessionId)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "거부 처리 실패")
    }
  }

  function handleComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      void handleSend()
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
          <SessionSidebar
            currentSessionId={currentSessionId}
            currentSessionTitle={currentSessionTitle}
            sessionTitleInput={sessionTitleInput}
            sessions={sessions}
            sectionOpen={{
              currentSession: sectionOpen.currentSession,
              sessionList: sectionOpen.sessionList,
            }}
            onToggleSection={toggleSection}
            onSessionTitleChange={setSessionTitleInput}
            onRenameCurrentSession={handleRenameCurrentSession}
            onDeleteCurrentSession={handleDeleteCurrentSession}
            onCreateSession={handleCreateSession}
            onSelectSession={handleSelectSession}
          />
        ) : null}

        <ChatPanel
          error={error}
          messages={messages}
          toolLogs={toolLogs}
          approvals={approvals}
          toolLogsOpen={sectionOpen.toolLogs}
          onToggleToolLogs={() => toggleSection("toolLogs")}
          messagesEndRef={messagesEndRef}
          input={input}
          loading={loading}
          onInputChange={setInput}
          onComposerKeyDown={handleComposerKeyDown}
          onSend={() => {
            void handleSend()
          }}
        />

        {rightSidebarOpen ? (
          <OperationsSidebar
            currentSessionId={currentSessionId}
            approvals={approvals}
            workspaceState={workspaceState}
            toolPanel={toolPanel}
            memorySuggestions={memorySuggestions}
            memories={memories}
            sectionOpen={{
              approvals: sectionOpen.approvals,
              workspace: sectionOpen.workspace,
              resources: sectionOpen.resources,
              suggestions: sectionOpen.suggestions,
              memories: sectionOpen.memories,
            }}
            isSyncing={isSyncing}
            memoryContentInput={memoryContentInput}
            memoryTagsInput={memoryTagsInput}
            memoryImportanceInput={memoryImportanceInput}
            memoryTypeInput={memoryTypeInput}
            onToggleSection={toggleSection}
            onManualSync={handleManualSync}
            onApprove={handleApprove}
            onReject={handleReject}
            onSaveSuggestion={handleSaveSuggestion}
            onDropSuggestion={handleDropSuggestion}
            onMemoryContentChange={setMemoryContentInput}
            onMemoryTagsChange={setMemoryTagsInput}
            onMemoryImportanceChange={setMemoryImportanceInput}
            onMemoryTypeChange={setMemoryTypeInput}
            onCreateMemory={handleCreateMemory}
            onUpdateMemory={handleUpdateMemory}
            onDeleteMemory={handleDeleteMemory}
          />
        ) : null}
      </div>
    </>
  )
}
