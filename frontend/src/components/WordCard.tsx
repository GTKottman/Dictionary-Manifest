import { useState } from 'react'
import type { Collection, WordOut } from '../types'

interface Props {
  word: WordOut
  collections: Collection[]
  activeCollectionId: number | null
  onAddToCollection: (word: WordOut, collectionId: number) => void
  onSetActiveCollection: (id: number) => void
}

function getFreqClass(freq: number | null): string {
  if (freq === null) return 'freq-unknown'
  if (freq >= 10) return 'freq-common'
  if (freq >= 2) return 'freq-med'
  return 'freq-rare'
}

function getFreqLabel(freq: number | null): string {
  if (freq === null) return 'Freq: unknown'
  if (freq >= 10) return `Common (${freq.toFixed(1)})`
  if (freq >= 2) return `Medium (${freq.toFixed(1)})`
  return `Rare (${freq.toFixed(2)})`
}

function formatStress(pattern: string | null): string {
  if (!pattern) return ''
  return pattern
    .split('')
    .map((c) => (c === '1' ? '◆' : c === '0' ? '◇' : '▸'))
    .join('')
}

function parseDef(def: string): { pos: string; text: string } {
  const idx = def.indexOf('\t')
  if (idx === -1) return { pos: '', text: def }
  return { pos: def.slice(0, idx), text: def.slice(idx + 1) }
}

function getPosFromTags(tags: string[]): string {
  const posMap: Record<string, string> = { n: 'n', v: 'v', adj: 'adj', adv: 'adv' }
  for (const t of tags) {
    const base = t.split(':')[0]
    if (posMap[base]) return posMap[base]
  }
  return ''
}

export default function WordCard({
  word,
  collections,
  activeCollectionId,
  onAddToCollection,
  onSetActiveCollection,
}: Props) {
  const [expanded, setExpanded] = useState(false)
  const [addMenuOpen, setAddMenuOpen] = useState(false)
  const [copied, setCopied] = useState(false)

  const syllables = word.syllables_cmu ?? word.syllables
  const pos = getPosFromTags(word.tags)
  const firstDef = word.defs[0] ? parseDef(word.defs[0]) : null

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(word.word)
      setCopied(true)
      setTimeout(() => setCopied(false), 1200)
    } catch {
      //
    }
  }

  const handleAddClick = () => {
    if (collections.length === 0) return
    if (collections.length === 1) {
      onAddToCollection(word, collections[0].id)
      return
    }
    if (activeCollectionId != null) {
      onAddToCollection(word, activeCollectionId)
    } else {
      setAddMenuOpen(!addMenuOpen)
    }
  }

  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData('application/json', JSON.stringify(word))
    e.dataTransfer.effectAllowed = 'copy'
  }

  return (
    <div
      className={`word-card ${expanded ? 'expanded' : ''}`}
      draggable
      onDragStart={handleDragStart}
    >
      <div className="word-card-top">
        <span
          className="word-text"
          onClick={handleCopy}
          title="Click to copy"
        >
          {copied ? '✓ copied' : word.word}
        </span>

        {word.stress_pattern && (
          <span className="word-stress" title={`Stress: ${word.stress_pattern}`}>
            {formatStress(word.stress_pattern)}
          </span>
        )}

        <div className="word-meta">
          {syllables != null && (
            <span className="syl-badge" title={`${syllables} syllables`}>
              {syllables} syl
            </span>
          )}
          {pos && <span className="pos-tag">{pos}</span>}
          <span
            className={`freq-dot ${getFreqClass(word.frequency)}`}
            title={getFreqLabel(word.frequency)}
          />
        </div>

        <div className="word-card-actions">
          {collections.length > 0 && (
            <div style={{ position: 'relative' }}>
              <button
                className="add-to-collection-btn"
                onClick={handleAddClick}
                title="Add to collection"
              >
                + Save
              </button>
              {addMenuOpen && (
                <div
                  style={{
                    position: 'absolute',
                    right: 0,
                    top: '110%',
                    background: 'var(--surface)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-sm)',
                    boxShadow: 'var(--shadow-md)',
                    zIndex: 50,
                    minWidth: 160,
                  }}
                >
                  {collections.map((col) => (
                    <button
                      key={col.id}
                      style={{
                        display: 'block',
                        width: '100%',
                        textAlign: 'left',
                        padding: '0.5rem 0.75rem',
                        fontSize: '0.82rem',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text)',
                        cursor: 'pointer',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-subtle)')}
                      onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                      onClick={() => {
                        onAddToCollection(word, col.id)
                        onSetActiveCollection(col.id)
                        setAddMenuOpen(false)
                      }}
                    >
                      {col.name}
                    </button>
                  ))}
                  <div
                    style={{ height: 1, background: 'var(--border)', margin: '0.25rem 0' }}
                  />
                  <button
                    style={{
                      display: 'block',
                      width: '100%',
                      textAlign: 'left',
                      padding: '0.5rem 0.75rem',
                      fontSize: '0.82rem',
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--muted)',
                      cursor: 'pointer',
                    }}
                    onClick={() => setAddMenuOpen(false)}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          )}
          <button
            className="expand-btn"
            onClick={() => setExpanded(!expanded)}
            title={expanded ? 'Collapse' : 'Expand details'}
          >
            {expanded ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {!expanded && firstDef && (
        <div className="word-def-preview">{firstDef.text}</div>
      )}

      {expanded && (
        <div className="word-card-details">
          {word.defs.length > 0 && (
            <div>
              <div className="detail-section-title">Definitions</div>
              <div className="def-list">
                {word.defs.map((d, i) => {
                  const { pos: p, text } = parseDef(d)
                  return (
                    <div key={i} className="def-item">
                      {p && <span className="def-pos">{p}.</span>}
                      {text}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {word.phonemes && word.phonemes.length > 0 && (
            <div>
              <div className="detail-section-title">Phonemes</div>
              <div className="phoneme-display">
                {word.phonemes.map((ph, i) => {
                  const isStressed = ph.endsWith('1') || ph.endsWith('2')
                  return (
                    <span key={i} className={`phoneme-badge ${isStressed ? 'stressed' : ''}`}>
                      {ph}
                    </span>
                  )
                })}
              </div>
              {word.stress_pattern && (
                <div style={{ marginTop: '0.3rem', fontSize: '0.78rem', color: 'var(--muted)' }}>
                  Pattern: <code style={{ fontFamily: 'var(--mono)' }}>{word.stress_pattern}</code>
                  {' '}&mdash; {formatStress(word.stress_pattern)}
                </div>
              )}
            </div>
          )}

          {word.score != null && (
            <div style={{ fontSize: '0.78rem', color: 'var(--muted)' }}>
              Relevance score: {word.score.toLocaleString()}
              {word.frequency != null && (
                <span style={{ marginLeft: '0.75rem' }}>
                  · Corpus frequency: {word.frequency.toFixed(2)}
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
