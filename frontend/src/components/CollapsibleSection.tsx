import type { ReactNode } from "react"

type CollapsibleSectionProps = {
  title: string
  isOpen: boolean
  onToggle: () => void
  actions?: ReactNode
  children: ReactNode
}

export function CollapsibleSection({
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
            onClick={(event) => event.stopPropagation()}
          >
            {actions}
          </div>
        ) : null}
      </div>

      {isOpen ? <div className="collapsible-body">{children}</div> : null}
    </section>
  )
}
