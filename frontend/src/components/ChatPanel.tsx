import type { KeyboardEvent, RefObject } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { ChatMessage, ToolLogItem } from "../types"
import { CollapsibleSection } from "./CollapsibleSection"

const PLANNER_TOOL_NAME = "__planner__"

type PlannerSummary = {
  used: boolean
  status: string
  tasks: string[]
}

type PendingApprovalSummary = {
  actionId?: string | null
  summary?: string | null
  message?: string | null
}

function getPlannerSummary(log: ToolLogItem | null): PlannerSummary | null {
  if (!log || log.tool_name !== PLANNER_TOOL_NAME) {
    return null
  }

  const used = Boolean(log.arguments.used)
  const status =
    typeof log.arguments.status === "string" ? log.arguments.status : "unknown"
  const rawTasks = log.arguments.tasks
  const tasks = Array.isArray(rawTasks)
    ? rawTasks.filter((item): item is string => typeof item === "string")
    : []

  return { used, status, tasks }
}

function parsePendingApproval(rawText: string): PendingApprovalSummary | null {
  if (!rawText.startsWith("__PENDING_APPROVAL__")) {
    return null
  }

  const data: Record<string, string> = {}
  for (const line of rawText.split("\n").slice(1)) {
    const separatorIndex = line.indexOf("=")
    if (separatorIndex < 0) continue
    const key = line.slice(0, separatorIndex).trim()
    const value = line.slice(separatorIndex + 1).trim()
    if (!key) continue
    data[key] = value
  }

  return {
    actionId: data.action_id ?? null,
    summary: data.summary ?? null,
    message: data.message ?? null,
  }
}

function getExecutionStatus(rawText: string): "ok" | "error" | "pending_approval" {
  if (parsePendingApproval(rawText)) {
    return "pending_approval"
  }
  if (rawText.trim().startsWith("ERROR:")) {
    return "error"
  }
  return "ok"
}

function getExecutionStatusLabel(rawText: string): string {
  const status = getExecutionStatus(rawText)
  if (status === "pending_approval") {
    return "승인 대기"
  }
  if (status === "error") {
    return "실행 오류"
  }
  return "실행 완료"
}

type ChatPanelProps = {
  error: string | null
  messages: ChatMessage[]
  toolLogs: ToolLogItem[]
  toolLogsOpen: boolean
  onToggleToolLogs: () => void
  messagesEndRef: RefObject<HTMLDivElement>
  input: string
  loading: boolean
  onInputChange: (value: string) => void
  onComposerKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void
  onSend: () => void
}

export function ChatPanel({
  error,
  messages,
  toolLogs,
  toolLogsOpen,
  onToggleToolLogs,
  messagesEndRef,
  input,
  loading,
  onInputChange,
  onComposerKeyDown,
  onSend,
}: ChatPanelProps) {
  const plannerLog =
    toolLogs
      .slice()
      .reverse()
      .find((log) => log.tool_name === PLANNER_TOOL_NAME) ?? null
  const planSummary = getPlannerSummary(plannerLog)
  const actualToolLogs = toolLogs.filter((log) => log.tool_name !== PLANNER_TOOL_NAME)
  const latestToolLog =
    actualToolLogs.length > 0 ? actualToolLogs[actualToolLogs.length - 1] : null
  const pendingApproval = latestToolLog
    ? parsePendingApproval(latestToolLog.result_raw)
    : null

  return (
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
                message.role === "user"
                  ? "message user-message"
                  : "message assistant-message"
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

      {planSummary?.used && planSummary.tasks.length > 0 ? (
        <div className="plan-summary-box">
          <div className="summary-title-row">
            <span className="summary-title">현재 계획</span>
            <span className="status-badge planned">계획됨</span>
          </div>
          <ol className="summary-task-list">
            {planSummary.tasks.map((task, index) => (
              <li key={`${task}-${index}`}>{task}</li>
            ))}
          </ol>
        </div>
      ) : null}

      {pendingApproval && latestToolLog ? (
        <div className="pending-banner">
          <div className="summary-title-row">
            <span className="summary-title">승인 대기 중</span>
            <span className="status-badge pending">승인 필요</span>
          </div>
          <div className="pending-banner-tool">
            tool: {latestToolLog.tool_name}
          </div>
          {pendingApproval.summary ? (
            <div className="pending-banner-summary">{pendingApproval.summary}</div>
          ) : null}
          {pendingApproval.actionId ? (
            <div className="pending-banner-meta">
              action_id: {pendingApproval.actionId}
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="tool-log-section">
        <CollapsibleSection
          title="툴 실행 로그"
          isOpen={toolLogsOpen}
          onToggle={onToggleToolLogs}
        >
          {actualToolLogs.length === 0 ? (
            <div className="empty-box">기록된 툴 실행 로그가 없습니다.</div>
          ) : (
            <div className="tool-log-list">
              {actualToolLogs
                .slice()
                .reverse()
                .map((log, index) => (
                  <div key={`${log.timestamp}-${index}`} className="tool-log-card">
                    <div className="tool-log-top">
                      <span>{log.tool_name}</span>
                      <div className="tool-log-status-group">
                        <span
                          className={`status-badge ${getExecutionStatus(log.result_raw)}`}
                        >
                          {getExecutionStatusLabel(log.result_raw)}
                        </span>
                        <span>step {log.step_index}</span>
                      </div>
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
          onChange={(event) => onInputChange(event.target.value)}
          onKeyDown={onComposerKeyDown}
          placeholder="메시지를 입력하세요"
          rows={5}
        />
        <button onClick={onSend} disabled={loading}>
          {loading ? "전송 중..." : "보내기"}
        </button>
      </div>
    </main>
  )
}
