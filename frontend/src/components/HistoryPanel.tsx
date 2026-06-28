import type { HistoryEntry, SearchRequest } from '../types'

interface Props {
  history: HistoryEntry[]
  open: boolean
  onToggle: () => void
  onReplay: (query: Partial<SearchRequest>) => void
  onDelete: (id: number) => void
}

function formatTime(isoStr: string): string {
  try {
    const d = new Date(isoStr + 'Z')
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

function queryLabel(query: Partial<SearchRequest>): string {
  const parts: string[] = []
  if (query.theme) parts.push(query.theme)
  if (query.emotions?.length) parts.push(`[${query.emotions.slice(0, 2).join(', ')}]`)
  if (query.rhyme_with) parts.push(`rhymes:${query.rhyme_with}`)
  if (query.starts_with || query.ends_with || query.contains || query.spelling_pattern) {
    parts.push('pattern')
  }
  return parts.join(' · ') || 'Search'
}

export default function HistoryPanel({ history, open, onToggle, onReplay, onDelete }: Props) {
  if (!open) {
    return (
      <div className="history-strip">
        <button
          className="history-label"
          style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--muted)' }}
          onClick={onToggle}
          title="Show search history"
        >
          History ▲
        </button>
        <div className="history-scroll">
          {history.slice(0, 20).map((entry) => (
            <button
              key={entry.id}
              className="history-pill"
              onClick={() => onReplay(entry.query)}
              title={`Re-run: ${queryLabel(entry.query)}`}
            >
              {queryLabel(entry.query)}
              <span className="history-pill-count">{entry.result_count}</span>
            </button>
          ))}
          {history.length === 0 && (
            <span style={{ fontSize: '0.75rem', color: 'var(--muted-light)' }}>
              Your recent searches will appear here
            </span>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="history-strip expanded">
      <div className="history-expanded-header">
        <span className="history-label">Search History</span>
        <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>{history.length} entries</span>
          <button className="btn btn-ghost btn-sm" onClick={onToggle}>
            Collapse ▼
          </button>
        </div>
      </div>
      <div className="history-expanded-body">
        {history.length === 0 && (
          <div style={{ width: '100%', textAlign: 'center', color: 'var(--muted)', fontSize: '0.82rem', padding: '1rem' }}>
            No history yet. Search something!
          </div>
        )}
        {history.map((entry) => (
          <div
            key={entry.id}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.3rem',
              border: '1px solid var(--border)',
              borderRadius: 99,
              padding: '0.2rem 0.5rem 0.2rem 0.65rem',
              background: 'var(--surface)',
              fontSize: '0.75rem',
            }}
          >
            <button
              style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 0 }}
              onClick={() => onReplay(entry.query)}
              title={`Re-run search`}
            >
              {queryLabel(entry.query)}
            </button>
            <span style={{ color: 'var(--muted-light)', fontSize: '0.68rem' }}>
              {entry.result_count} · {formatTime(entry.created_at)}
            </span>
            <button
              style={{ background: 'transparent', border: 'none', color: 'var(--muted-light)', cursor: 'pointer', padding: '0 0.1rem', fontSize: '0.85rem' }}
              onClick={() => onDelete(entry.id)}
              title="Remove from history"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
