import { useState } from 'react'
import type { Collection, SearchResponse, WordOut } from '../types'
import WordCard from './WordCard'

interface Props {
  results: SearchResponse | null
  isSearching: boolean
  error: string | null
  sourcesRevealed: boolean
  onToggleSources: () => void
  collections: Collection[]
  activeCollectionId: number | null
  onAddToCollection: (word: WordOut, collectionId: number) => void
  onSetActiveCollection: (id: number) => void
}

function copyWords(words: WordOut[]) {
  navigator.clipboard.writeText(words.map((w) => w.word).join('\n')).catch(() => {})
}

function copyTsv(words: WordOut[]) {
  const header = 'Word\tSyllables\tStress\tFrequency\tDefinition'
  const rows = words.map((w) => {
    const syl = w.syllables_cmu ?? w.syllables ?? ''
    const stress = w.stress_pattern ?? ''
    const freq = w.frequency?.toFixed(2) ?? ''
    const def = (w.defs[0] ?? '').split('\t').slice(1).join(' ')
    return `${w.word}\t${syl}\t${stress}\t${freq}\t${def}`
  })
  navigator.clipboard.writeText([header, ...rows].join('\n')).catch(() => {})
}

function BankActions({ words, label }: { words: WordOut[]; label: string }) {
  const [wCopied, setWCopied] = useState(false)
  const [tCopied, setTCopied] = useState(false)

  return (
    <div className="bank-actions">
      <button
        className="btn btn-secondary btn-sm"
        onClick={() => {
          copyWords(words)
          setWCopied(true)
          setTimeout(() => setWCopied(false), 1400)
        }}
      >
        {wCopied ? '✓ Copied' : 'Copy words'}
      </button>
      <button
        className="btn btn-secondary btn-sm"
        onClick={() => {
          copyTsv(words)
          setTCopied(true)
          setTimeout(() => setTCopied(false), 1400)
        }}
      >
        {tCopied ? '✓ Copied' : 'Copy TSV'}
      </button>
    </div>
  )
}

function Bank({
  words,
  label,
  source,
  sourcesRevealed,
  collections,
  activeCollectionId,
  onAddToCollection,
  onSetActiveCollection,
}: {
  words: WordOut[]
  label: string
  source: string
  sourcesRevealed: boolean
  collections: Collection[]
  activeCollectionId: number | null
  onAddToCollection: (word: WordOut, collectionId: number) => void
  onSetActiveCollection: (id: number) => void
}) {
  return (
    <div className="bank-panel">
      <div className="bank-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span className="bank-title">{label}</span>
          <span className="bank-count">{words.length} words</span>
          {sourcesRevealed && source && (
            <span className="bank-source-badge">
              {source === 'datamuse' ? 'Datamuse' : source === 'wiktionary' ? 'Wiktionary' : source}
            </span>
          )}
        </div>
        <BankActions words={words} label={label} />
      </div>

      {words.length === 0 ? (
        <div className="bank-empty">No words matched for this list.</div>
      ) : (
        <div className="word-cards">
          {words.map((w) => (
            <WordCard
              key={w.word}
              word={w}
              collections={collections}
              activeCollectionId={activeCollectionId}
              onAddToCollection={onAddToCollection}
              onSetActiveCollection={onSetActiveCollection}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function ResultsArea({
  results,
  isSearching,
  error,
  sourcesRevealed,
  onToggleSources,
  collections,
  activeCollectionId,
  onAddToCollection,
  onSetActiveCollection,
}: Props) {
  if (isSearching) {
    return (
      <div className="search-loading">
        <span className="loading-spinner" />
        Searching across word banks…
      </div>
    )
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>
  }

  if (!results) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📖</div>
        <div className="empty-state-title">Ready to search</div>
        <div className="empty-state-desc">
          Enter a theme, add moods and sound constraints, then hit Find Words. Results appear in two
          side-by-side lists so you can compare different word sources blind.
        </div>
      </div>
    )
  }

  const { bank_a, bank_b, bank_a_source, bank_b_source, info, warnings } = results

  return (
    <div>
      {info && <div className="alert alert-info" style={{ marginBottom: '1rem' }}>{info}</div>}

      {warnings.length > 0 && (
        <div className="alert alert-warn" style={{ marginBottom: '1rem' }}>
          {warnings.map((w, i) => <div key={i}>{w}</div>)}
        </div>
      )}

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1rem',
          flexWrap: 'wrap',
          gap: '0.5rem',
        }}
      >
        <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text)' }}>
          Results
          <span style={{ fontWeight: 400, color: 'var(--muted)', marginLeft: '0.5rem', fontSize: '0.82rem' }}>
            {bank_a.length + bank_b.length} total words across two lists
          </span>
        </div>
        <button
          className={`reveal-btn ${sourcesRevealed ? 'revealed' : ''}`}
          onClick={onToggleSources}
          title="Reveal which list came from which source"
        >
          {sourcesRevealed ? '◆ Sources revealed' : '◇ Reveal sources'}
        </button>
      </div>

      <div className="banks-grid">
        <Bank
          words={bank_a}
          label="List 1"
          source={bank_a_source}
          sourcesRevealed={sourcesRevealed}
          collections={collections}
          activeCollectionId={activeCollectionId}
          onAddToCollection={onAddToCollection}
          onSetActiveCollection={onSetActiveCollection}
        />
        <Bank
          words={bank_b}
          label="List 2"
          source={bank_b_source}
          sourcesRevealed={sourcesRevealed}
          collections={collections}
          activeCollectionId={activeCollectionId}
          onAddToCollection={onAddToCollection}
          onSetActiveCollection={onSetActiveCollection}
        />
      </div>
    </div>
  )
}
