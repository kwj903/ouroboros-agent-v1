import { CollapsibleSection } from "./CollapsibleSection"
import type {
  ApprovalItem,
  MemoryItem,
  MemorySuggestionItem,
  ToolPanelData,
  WorkspaceState,
} from "../types"

type OperationsSidebarProps = {
  currentSessionId: string | null
  approvals: ApprovalItem[]
  workspaceState: WorkspaceState | null
  toolPanel: ToolPanelData | null
  memorySuggestions: MemorySuggestionItem[]
  memories: MemoryItem[]
  sectionOpen: {
    approvals: boolean
    workspace: boolean
    resources: boolean
    suggestions: boolean
    memories: boolean
  }
  isSyncing: boolean
  memoryContentInput: string
  memoryTagsInput: string
  memoryImportanceInput: number
  memoryTypeInput: string
  onToggleSection: (
    key: "approvals" | "workspace" | "resources" | "suggestions" | "memories",
  ) => void
  onManualSync: () => void
  onApprove: (actionId: string) => void
  onReject: (actionId: string) => void
  onSaveSuggestion: (suggestionId: string) => void
  onDropSuggestion: (suggestionId: string) => void
  onMemoryContentChange: (value: string) => void
  onMemoryTagsChange: (value: string) => void
  onMemoryImportanceChange: (value: number) => void
  onMemoryTypeChange: (value: string) => void
  onCreateMemory: () => void
  onUpdateMemory: (memory: MemoryItem) => void
  onDeleteMemory: (memoryId: string) => void
}

function getApprovalLabel(item: ApprovalItem): string {
  switch (item.action_type) {
    case "create_file":
      return "빈 파일 생성"
    case "write_file":
      return "파일 쓰기"
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

function getPlannerStatusLabel(status: string): string {
  switch (status) {
    case "planned":
      return "계획됨"
    case "fallback":
      return "직접 실행"
    case "invalid":
      return "계획 보정"
    default:
      return status
  }
}

function getExecutionStatusLabel(resultKind: string): string {
  switch (resultKind) {
    case "pending_approval":
      return "승인 필요"
    case "error":
      return "실행 오류"
    default:
      return "실행 완료"
  }
}

export function OperationsSidebar({
  currentSessionId,
  approvals,
  workspaceState,
  toolPanel,
  memorySuggestions,
  memories,
  sectionOpen,
  isSyncing,
  memoryContentInput,
  memoryTagsInput,
  memoryImportanceInput,
  memoryTypeInput,
  onToggleSection,
  onManualSync,
  onApprove,
  onReject,
  onSaveSuggestion,
  onDropSuggestion,
  onMemoryContentChange,
  onMemoryTagsChange,
  onMemoryImportanceChange,
  onMemoryTypeChange,
  onCreateMemory,
  onUpdateMemory,
  onDeleteMemory,
}: OperationsSidebarProps) {
  return (
    <aside className="panel side-panel right-panel">
      <div className="inline-actions" style={{ marginBottom: 10 }}>
        <button onClick={onManualSync} disabled={isSyncing}>
          {isSyncing ? "동기화 중..." : "동기화"}
        </button>
      </div>

      <div className="sidebar-scroll">
        <CollapsibleSection
          title="계획 / 실행 요약"
          isOpen={sectionOpen.resources}
          onToggle={() => onToggleSection("resources")}
        >
          {!currentSessionId ? (
            <div className="empty-box">선택된 세션이 없습니다.</div>
          ) : !toolPanel ? (
            <div className="empty-box">표시할 요약 정보가 없습니다.</div>
          ) : (
            <div className="summary-panel">
              {toolPanel.plan_summary?.used &&
              toolPanel.plan_summary.tasks.length > 0 ? (
                <div className="summary-card">
                  <div className="summary-title-row">
                    <span className="summary-title">현재 계획</span>
                    <span className="status-badge planned">
                      {getPlannerStatusLabel(toolPanel.plan_summary.status)}
                    </span>
                  </div>
                  <ol className="summary-task-list">
                    {toolPanel.plan_summary.tasks.map((task, index) => (
                      <li key={`${task}-${index}`}>{task}</li>
                    ))}
                  </ol>
                </div>
              ) : null}

              {toolPanel.latest_execution ? (
                <div className="summary-card">
                  <div className="summary-title-row">
                    <span className="summary-title">최근 실행</span>
                    <span
                      className={`status-badge ${toolPanel.latest_execution.result_kind}`}
                    >
                      {getExecutionStatusLabel(toolPanel.latest_execution.result_kind)}
                    </span>
                  </div>
                  <div className="summary-meta-line">
                    tool: {toolPanel.latest_execution.tool_name}
                  </div>
                  <div className="summary-meta-line">
                    step: {toolPanel.latest_execution.step_index}
                  </div>
                  <div className="summary-preview">
                    {toolPanel.latest_execution.result_preview}
                  </div>
                </div>
              ) : null}

              {toolPanel.pending_approval ? (
                <div className="pending-banner sidebar-pending-banner">
                  <div className="summary-title-row">
                    <span className="summary-title">보류 중인 실행</span>
                    <span className="status-badge pending">승인 필요</span>
                  </div>
                  {toolPanel.pending_approval.summary ? (
                    <div className="pending-banner-summary">
                      {toolPanel.pending_approval.summary}
                    </div>
                  ) : null}
                  {toolPanel.pending_approval.action_id ? (
                    <div className="pending-banner-meta">
                      action_id: {toolPanel.pending_approval.action_id}
                    </div>
                  ) : null}
                  {toolPanel.pending_approval.message ? (
                    <div className="pending-banner-meta">
                      {toolPanel.pending_approval.message}
                    </div>
                  ) : null}
                </div>
              ) : null}

              {(toolPanel.last_note_search ||
                toolPanel.last_note_read ||
                toolPanel.last_file_read) ? (
                <div className="summary-card">
                  <div className="summary-title">최근 노트 / 파일 결과</div>
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
                                <div className="resource-meta">
                                  score: {item.score}
                                </div>
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
                  </div>
                </div>
              ) : null}

              {!toolPanel.plan_summary?.used &&
                !toolPanel.latest_execution &&
                !toolPanel.pending_approval &&
                !toolPanel.last_note_search &&
                !toolPanel.last_note_read &&
                !toolPanel.last_file_read && (
                  <div className="empty-box">표시할 실행 요약이 없습니다.</div>
                )}
            </div>
          )}
        </CollapsibleSection>

        <CollapsibleSection
          title="승인 대기"
          isOpen={sectionOpen.approvals}
          onToggle={() => onToggleSection("approvals")}
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
                    <button onClick={() => onApprove(item.action_id)}>승인</button>
                    <button
                      className="danger"
                      onClick={() => onReject(item.action_id)}
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
          onToggle={() => onToggleSection("workspace")}
        >
          {!currentSessionId ? (
            <div className="empty-box">선택된 세션이 없습니다.</div>
          ) : !workspaceState || Object.keys(workspaceState).length === 0 ? (
            <div className="empty-box">기록된 작업 상태가 없습니다.</div>
          ) : (
            <div className="workspace-card">
              {workspaceState.last_browsed_path && (
                <div className="workspace-row">
                  <span className="workspace-label">마지막 탐색</span>
                  <span className="workspace-value">
                    {workspaceState.last_browsed_path}
                  </span>
                </div>
              )}

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

              {workspaceState.last_requested_create_path && (
                <div className="workspace-row">
                  <span className="workspace-label">최근 생성 요청</span>
                  <span className="workspace-value">
                    {workspaceState.last_requested_create_path}
                  </span>
                </div>
              )}

              {workspaceState.last_requested_write_path && (
                <div className="workspace-row">
                  <span className="workspace-label">최근 쓰기 요청</span>
                  <span className="workspace-value">
                    {workspaceState.last_requested_write_path}
                  </span>
                </div>
              )}

              {workspaceState.last_requested_modify_path && (
                <div className="workspace-row">
                  <span className="workspace-label">최근 수정 요청</span>
                  <span className="workspace-value">
                    {workspaceState.last_requested_modify_path}
                  </span>
                </div>
              )}

              {workspaceState.last_requested_delete_path && (
                <div className="workspace-row">
                  <span className="workspace-label">최근 삭제 요청</span>
                  <span className="workspace-value">
                    {workspaceState.last_requested_delete_path}
                  </span>
                </div>
              )}
            </div>
          )}
        </CollapsibleSection>

        <CollapsibleSection
          title="기억 후보"
          isOpen={sectionOpen.suggestions}
          onToggle={() => onToggleSection("suggestions")}
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
                  <button onClick={() => onSaveSuggestion(item.suggestion_id)}>
                    저장
                  </button>
                  <button
                    className="danger"
                    onClick={() => onDropSuggestion(item.suggestion_id)}
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
          onToggle={() => onToggleSection("memories")}
        >
          <div className="memory-create-box">
            <textarea
              value={memoryContentInput}
              onChange={(event) => onMemoryContentChange(event.target.value)}
              placeholder="새 장기 기억 내용을 입력하세요"
              rows={4}
            />
            <input
              value={memoryTagsInput}
              onChange={(event) => onMemoryTagsChange(event.target.value)}
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
                  onChange={(event) => onMemoryImportanceChange(Number(event.target.value))}
                />
              </label>
              <label>
                타입
                <input
                  value={memoryTypeInput}
                  onChange={(event) => onMemoryTypeChange(event.target.value)}
                />
              </label>
            </div>
            <button onClick={onCreateMemory}>장기 기억 추가</button>
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
                  <button onClick={() => onUpdateMemory(memory)}>수정</button>
                  <button
                    className="danger"
                    onClick={() => onDeleteMemory(memory.memory_id)}
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
  )
}
