import { useState } from 'react'
import type { PhoneticMode, PosFilter, SearchRequest } from '../types'
import MoodPalette from './MoodPalette'

interface Props {
  params: SearchRequest
  onChange: (p: Partial<SearchRequest>) => void
  onSearch: () => void
  isSearching: boolean
}

function Section({
  title,
  children,
  defaultOpen = true,
}: {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="form-section">
      <div className="form-section-header" onClick={() => setOpen(!open)}>
        <span className="form-section-title">{title}</span>
        <span className={`form-section-chevron ${open ? 'open' : ''}`}>▲</span>
      </div>
      {open && <div className="form-section-body">{children}</div>}
    </div>
  )
}

const PHONETIC_MODES: { id: PhoneticMode; label: string; title: string }[] = [
  { id: 'none', label: 'Off', title: 'No phonetic filtering' },
  { id: 'assonance', label: 'Assonance', title: 'Same stressed vowel sounds' },
  { id: 'alliteration', label: 'Alliter.', title: 'Same starting consonant sounds' },
  { id: 'consonance', label: 'Consonance', title: 'Same consonant sounds throughout' },
]

const POS_OPTIONS: { value: PosFilter; label: string }[] = [
  { value: '', label: 'Any part of speech' },
  { value: 'n', label: 'Noun' },
  { value: 'v', label: 'Verb' },
  { value: 'adj', label: 'Adjective' },
  { value: 'adv', label: 'Adverb' },
]

export default function SearchPanel({ params, onChange, onSearch, isSearching }: Props) {
  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') onSearch()
  }

  return (
    <>
      {/* Theme — always visible, no collapsible */}
      <div>
        <div className="field-label">
          Theme <span className="req">*</span>
        </div>
        <input
          className="text-input"
          placeholder="e.g. horror, longing, redemption"
          value={params.theme}
          onChange={(e) => onChange({ theme: e.target.value })}
          onKeyDown={handleKey}
          autoFocus
        />
        {params.topics && (
          <input
            className="text-input"
            style={{ marginTop: '0.4rem' }}
            placeholder="Extra topics (comma separated)"
            value={params.topics}
            onChange={(e) => onChange({ topics: e.target.value })}
            onKeyDown={handleKey}
          />
        )}
        {!params.topics && (
          <button
            className="btn btn-ghost btn-sm"
            style={{ marginTop: '0.3rem', paddingLeft: 0 }}
            onClick={() => onChange({ topics: ' ' })}
          >
            + Add topics
          </button>
        )}
      </div>

      <Section title="Mood / Emotion">
        <MoodPalette
          selected={params.emotions}
          onChange={(emotions) => onChange({ emotions })}
        />
      </Section>

      <Section title="Spelling Shape" defaultOpen={false}>
        <div>
          <div className="field-label">Raw pattern <span className="hint">(* = any letters, ? = one)</span></div>
          <input
            className="text-input"
            placeholder="e.g. *ness or s?ng"
            value={params.spelling_pattern}
            onChange={(e) => onChange({ spelling_pattern: e.target.value })}
            onKeyDown={handleKey}
          />
        </div>
        <div style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--muted)' }}>— or use helpers —</div>
        <div className="field-row-3">
          <div>
            <div className="field-label">Starts with</div>
            <input
              className="text-input"
              placeholder="un…"
              value={params.starts_with}
              onChange={(e) => onChange({ starts_with: e.target.value })}
              onKeyDown={handleKey}
              disabled={!!params.spelling_pattern.trim()}
            />
          </div>
          <div>
            <div className="field-label">Contains</div>
            <input
              className="text-input"
              placeholder="…ow…"
              value={params.contains}
              onChange={(e) => onChange({ contains: e.target.value })}
              onKeyDown={handleKey}
              disabled={!!params.spelling_pattern.trim()}
            />
          </div>
          <div>
            <div className="field-label">Ends with</div>
            <input
              className="text-input"
              placeholder="…ing"
              value={params.ends_with}
              onChange={(e) => onChange({ ends_with: e.target.value })}
              onKeyDown={handleKey}
              disabled={!!params.spelling_pattern.trim()}
            />
          </div>
        </div>
      </Section>

      <Section title="Sound" defaultOpen={false}>
        <div>
          <div className="field-label">Rhymes with</div>
          <input
            className="text-input"
            placeholder="e.g. night"
            value={params.rhyme_with}
            onChange={(e) => onChange({ rhyme_with: e.target.value })}
            onKeyDown={handleKey}
          />
        </div>
        <div>
          <div className="field-label">Sounds like</div>
          <input
            className="text-input"
            placeholder="e.g. storm (phonetic)"
            value={params.sounds_like}
            onChange={(e) => onChange({ sounds_like: e.target.value })}
            onKeyDown={handleKey}
          />
        </div>
      </Section>

      <Section title="Syllables + Meter" defaultOpen={false}>
        <div>
          <div className="field-label">Syllable count range</div>
          <div className="range-row">
            <span className="range-label">Min</span>
            <input
              className="num-input"
              type="number"
              min={1}
              max={20}
              value={params.syllable_min ?? ''}
              placeholder="—"
              onChange={(e) => onChange({ syllable_min: e.target.value ? Number(e.target.value) : null })}
            />
            <span className="range-label">Max</span>
            <input
              className="num-input"
              type="number"
              min={1}
              max={20}
              value={params.syllable_max ?? ''}
              placeholder="—"
              onChange={(e) => onChange({ syllable_max: e.target.value ? Number(e.target.value) : null })}
            />
          </div>
        </div>
        <div>
          <div className="field-label">
            Stress pattern <span className="hint">(1=stressed, 0=unstressed, e.g. 10 = iambic)</span>
          </div>
          <input
            className="text-input"
            placeholder="e.g. 10, 010, 100"
            value={params.stress_pattern}
            onChange={(e) => onChange({ stress_pattern: e.target.value.replace(/[^012]/g, '') })}
            onKeyDown={handleKey}
            style={{ fontFamily: 'var(--mono)' }}
          />
        </div>
      </Section>

      <Section title="Phonetic Match" defaultOpen={false}>
        <div>
          <div className="field-label">Mode</div>
          <div className="phonetic-tabs">
            {PHONETIC_MODES.map((m) => (
              <button
                key={m.id}
                className={`phonetic-tab ${params.phonetic_match === m.id ? 'active' : ''}`}
                onClick={() => onChange({ phonetic_match: m.id })}
                title={m.title}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>
        {params.phonetic_match !== 'none' && (
          <div>
            <div className="field-label">Anchor word <span className="hint">(match results to this word's sounds)</span></div>
            <input
              className="text-input"
              placeholder="e.g. rain"
              value={params.phonetic_anchor}
              onChange={(e) => onChange({ phonetic_anchor: e.target.value })}
              onKeyDown={handleKey}
            />
          </div>
        )}
      </Section>

      <Section title="Refine" defaultOpen={false}>
        <div>
          <div className="field-label">Part of speech</div>
          <select
            className="select-input"
            value={params.pos_filter}
            onChange={(e) => onChange({ pos_filter: e.target.value as PosFilter })}
          >
            {POS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <div className="field-label">Max results <span className="hint">(1–100)</span></div>
          <input
            className="num-input"
            type="number"
            min={1}
            max={100}
            value={params.max_results}
            onChange={(e) => onChange({ max_results: Math.max(1, Math.min(100, Number(e.target.value))) })}
            style={{ width: '80px' }}
          />
        </div>
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={params.prefer_common}
            onChange={(e) => onChange({ prefer_common: e.target.checked })}
          />
          Prefer common / high-frequency words
        </label>
      </Section>

      <button
        className="btn btn-primary btn-full btn-search"
        onClick={onSearch}
        disabled={isSearching}
      >
        {isSearching ? (
          <>
            <span className="loading-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
            Searching…
          </>
        ) : (
          'Find Words'
        )}
      </button>
    </>
  )
}
