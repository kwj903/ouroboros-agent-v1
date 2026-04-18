import { CollapsibleSection } from "./CollapsibleSection"
import type { SessionItem } from "../types"

type SessionSidebarProps = {
  currentSessionId: string | null
  currentSessionTitle: string
  sessionTitleInput: string
  sessions: SessionItem[]
  sectionOpen: {
    currentSession: boolean
    sessionList: boolean
  }
  onToggleSection: (key: "currentSession" | "sessionList") => void
  onSessionTitleChange: (value: string) => void
  onRenameCurrentSession: () => void
  onDeleteCurrentSession: () => void
  onCreateSession: () => void
  onSelectSession: (sessionId: string) => void
}

export function SessionSidebar({
  currentSessionId,
  currentSessionTitle,
  sessionTitleInput,
  sessions,
  sectionOpen,
  onToggleSection,
  onSessionTitleChange,
  onRenameCurrentSession,
  onDeleteCurrentSession,
  onCreateSession,
  onSelectSession,
}: SessionSidebarProps) {
  return (
    <aside className="panel side-panel left-panel">
      <div className="sidebar-scroll">
        <CollapsibleSection
          title="현재 세션"
          isOpen={sectionOpen.currentSession}
          onToggle={() => onToggleSection("currentSession")}
        >
          <div className="session-current">
            <div className="label">현재 세션</div>
            <div className="value">{currentSessionTitle}</div>
            <div className="subvalue">{currentSessionId ?? "-"}</div>

            <div className="session-edit-box">
              <input
                value={sessionTitleInput}
                onChange={(event) => onSessionTitleChange(event.target.value)}
                placeholder="세션 이름"
              />
              <div className="inline-actions">
                <button onClick={onRenameCurrentSession}>
                  이름 변경
                </button>
                <button
                  className="danger"
                  onClick={onDeleteCurrentSession}
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
          onToggle={() => onToggleSection("sessionList")}
          actions={<button onClick={onCreateSession}>새 세션</button>}
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
                onClick={() => onSelectSession(session.session_id)}
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
  )
}
