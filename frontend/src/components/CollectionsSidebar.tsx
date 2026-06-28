import { useEffect, useState } from 'react'
import * as api from '../api'
import type { Collection, CollectionWord, WordOut } from '../types'

interface Props {
  collections: Collection[]
  activeCollectionId: number | null
  onSetActive: (id: number | null) => void
  onCreate: (name: string) => void
  onDelete: (id: number) => void
  onWordDropped: (word: WordOut) => void
}

function DropZone({ collectionId, onDrop }: { collectionId: number; onDrop: (word: WordOut) => void }) {
  const [over, setOver] = useState(false)

  return (
    <div
      className={`drop-zone ${over ? 'drag-over' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setOver(true) }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setOver(false)
        try {
          const word: WordOut = JSON.parse(e.dataTransfer.getData('application/json'))
          onDrop(word)
        } catch { /* ignore */ }
      }}
    >
      Drag words here to add to this collection
    </div>
  )
}

function CollectionView({
  collection,
  onDelete,
  onWordDrop,
}: {
  collection: Collection
  onDelete: (id: number) => void
  onWordDrop: (word: WordOut) => void
}) {
  const [words, setWords] = useState<CollectionWord[]>([])
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    setLoading(true)
    api.getCollectionWords(collection.id)
      .then(setWords)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [collection.id, collection.word_count])

  const handleRemoveWord = async (word: string) => {
    await api.removeWordFromCollection(collection.id, word)
    setWords((prev) => prev.filter((w) => w.word !== word))
  }

  const handleExport = async (fmt: 'text' | 'tsv') => {
    setExporting(true)
    try {
      const res = await api.exportCollection(collection.id, fmt)
      await navigator.clipboard.writeText(res.content)
    } catch { /* ignore */ }
    setExporting(false)
  }

  return (
    <div className="collection-words-panel">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.4rem' }}>
        <span style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>{words.length} words</span>
        <div style={{ display: 'flex', gap: '0.3rem' }}>
          <button className="btn btn-ghost btn-sm" onClick={() => handleExport('text')} title="Copy words to clipboard">
            {exporting ? '…' : 'Copy words'}
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => handleExport('tsv')} title="Copy as TSV">
            TSV
          </button>
          <button
            className="btn btn-ghost btn-sm"
            style={{ color: 'var(--error)' }}
            onClick={() => {
              if (confirm(`Delete collection "${collection.name}"?`)) onDelete(collection.id)
            }}
            title="Delete collection"
          >
            🗑
          </button>
        </div>
      </div>

      <DropZone collectionId={collection.id} onDrop={onWordDrop} />

      {loading ? (
        <div style={{ textAlign: 'center', padding: '1rem', color: 'var(--muted)', fontSize: '0.82rem' }}>Loading…</div>
      ) : words.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '0.5rem', color: 'var(--muted)', fontSize: '0.82rem' }}>
          No words yet. Drag cards here or use "+ Save" on any word.
        </div>
      ) : (
        <div>
          {words.map((w) => (
            <div key={w.word} className="collection-word-row">
              <span className="collection-word-text">{w.word}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                {w.metadata.syllables_cmu != null && (
                  <span style={{ fontSize: '0.72rem', color: 'var(--muted)' }}>{String(w.metadata.syllables_cmu)}syl</span>
                )}
                <button
                  className="btn-icon"
                  style={{ fontSize: '0.8rem' }}
                  onClick={() => handleRemoveWord(w.word)}
                  title="Remove from collection"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function CollectionsSidebar({
  collections,
  activeCollectionId,
  onSetActive,
  onCreate,
  onDelete,
  onWordDropped,
}: Props) {
  const [newName, setNewName] = useState('')
  const [creating, setCreating] = useState(false)

  const handleCreate = async () => {
    const name = newName.trim()
    if (!name) return
    setCreating(true)
    try {
      await onCreate(name)
      setNewName('')
    } finally {
      setCreating(false)
    }
  }

  const activeCollection = collections.find((c) => c.id === activeCollectionId) ?? null

  return (
    <div className="collections-inner">
      <div className="collections-header">
        <span className="collections-title">Collections</span>
        <button
          className="btn-icon"
          style={{ fontSize: '1rem' }}
          onClick={() => {
            const name = prompt('Collection name:')
            if (name?.trim()) onCreate(name.trim())
          }}
          title="New collection"
        >
          +
        </button>
      </div>

      {collections.length === 0 ? (
        <div style={{ padding: '1rem 0.75rem', fontSize: '0.82rem', color: 'var(--muted)', lineHeight: 1.6 }}>
          No collections yet. Create one to start saving words.
        </div>
      ) : (
        <div className="collections-body">
          {collections.map((col) => (
            <div
              key={col.id}
              className={`collection-item ${col.id === activeCollectionId ? 'active' : ''}`}
              onClick={() => onSetActive(col.id === activeCollectionId ? null : col.id)}
            >
              <span className="collection-name" title={col.name}>{col.name}</span>
              <span className="collection-count">{col.word_count}</span>
            </div>
          ))}
        </div>
      )}

      {activeCollection && (
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', borderTop: '1px solid var(--border)' }}>
          <div style={{ padding: '0.5rem 0.75rem', background: 'var(--bg-subtle)', borderBottom: '1px solid var(--border)', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {activeCollection.name}
          </div>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            <CollectionView
              collection={activeCollection}
              onDelete={onDelete}
              onWordDrop={onWordDropped}
            />
          </div>
        </div>
      )}

      {/* Quick create at bottom */}
      <div style={{ padding: '0.6rem 0.75rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '0.4rem' }}>
        <input
          className="text-input"
          placeholder="New collection name…"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleCreate() }}
          style={{ fontSize: '0.82rem', padding: '0.35rem 0.55rem' }}
        />
        <button
          className="btn btn-primary btn-sm"
          onClick={handleCreate}
          disabled={!newName.trim() || creating}
        >
          +
        </button>
      </div>
    </div>
  )
}
