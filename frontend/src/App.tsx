import { useCallback, useEffect, useReducer, useRef, useState } from 'react'
import * as api from './api'
import CollectionsSidebar from './components/CollectionsSidebar'
import Header from './components/Header'
import HistoryPanel from './components/HistoryPanel'
import ResultsArea from './components/ResultsArea'
import SearchPanel from './components/SearchPanel'
import type {
  Collection,
  HistoryEntry,
  SearchRequest,
  SearchResponse,
  WordOut,
} from './types'
import { DEFAULT_SEARCH } from './types'

// ── Dark mode ──────────────────────────────────────────────────────
function getInitialTheme(): 'light' | 'dark' {
  const stored = localStorage.getItem('ls-theme') as 'light' | 'dark' | null
  if (stored) return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(theme: 'light' | 'dark') {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('ls-theme', theme)
}

// ── App State ──────────────────────────────────────────────────────
interface AppState {
  searchParams: SearchRequest
  results: SearchResponse | null
  isSearching: boolean
  searchError: string | null
  sourcesRevealed: boolean
  collectionsOpen: boolean
  historyOpen: boolean
  collections: Collection[]
  history: HistoryEntry[]
  activeCollectionId: number | null
  theme: 'light' | 'dark'
}

type AppAction =
  | { type: 'SET_PARAMS'; payload: Partial<SearchRequest> }
  | { type: 'SET_RESULTS'; payload: SearchResponse }
  | { type: 'SET_SEARCHING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'TOGGLE_SOURCES' }
  | { type: 'TOGGLE_COLLECTIONS' }
  | { type: 'TOGGLE_HISTORY' }
  | { type: 'SET_COLLECTIONS'; payload: Collection[] }
  | { type: 'SET_HISTORY'; payload: HistoryEntry[] }
  | { type: 'SET_ACTIVE_COLLECTION'; payload: number | null }
  | { type: 'TOGGLE_THEME' }

function reducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_PARAMS':
      return { ...state, searchParams: { ...state.searchParams, ...action.payload } }
    case 'SET_RESULTS':
      return { ...state, results: action.payload, searchError: null, sourcesRevealed: false }
    case 'SET_SEARCHING':
      return { ...state, isSearching: action.payload }
    case 'SET_ERROR':
      return { ...state, searchError: action.payload }
    case 'TOGGLE_SOURCES':
      return { ...state, sourcesRevealed: !state.sourcesRevealed }
    case 'TOGGLE_COLLECTIONS':
      return { ...state, collectionsOpen: !state.collectionsOpen }
    case 'TOGGLE_HISTORY':
      return { ...state, historyOpen: !state.historyOpen }
    case 'SET_COLLECTIONS':
      return { ...state, collections: action.payload }
    case 'SET_HISTORY':
      return { ...state, history: action.payload }
    case 'SET_ACTIVE_COLLECTION':
      return { ...state, activeCollectionId: action.payload }
    case 'TOGGLE_THEME': {
      const next = state.theme === 'dark' ? 'light' : 'dark'
      applyTheme(next)
      return { ...state, theme: next }
    }
    default:
      return state
  }
}

const initialTheme = getInitialTheme()
applyTheme(initialTheme)

const initialState: AppState = {
  searchParams: DEFAULT_SEARCH,
  results: null,
  isSearching: false,
  searchError: null,
  sourcesRevealed: false,
  collectionsOpen: true,
  historyOpen: false,
  collections: [],
  history: [],
  activeCollectionId: null,
  theme: initialTheme,
}

// ── Root Component ─────────────────────────────────────────────────
export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)
  const abortRef = useRef<AbortController | null>(null)

  // Load collections and history on mount
  useEffect(() => {
    api.getCollections().then((c) => dispatch({ type: 'SET_COLLECTIONS', payload: c })).catch(() => {})
    api.getHistory().then((h) => dispatch({ type: 'SET_HISTORY', payload: h })).catch(() => {})
  }, [])

  const handleSearch = useCallback(async (params?: SearchRequest) => {
    const p = params ?? state.searchParams
    if (!p.theme.trim()) {
      dispatch({ type: 'SET_ERROR', payload: 'Enter a theme to start searching.' })
      return
    }
    abortRef.current?.abort()
    dispatch({ type: 'SET_SEARCHING', payload: true })
    dispatch({ type: 'SET_ERROR', payload: null })
    try {
      const res = await api.search(p)
      dispatch({ type: 'SET_RESULTS', payload: res })
      // Refresh history after search
      api.getHistory().then((h) => dispatch({ type: 'SET_HISTORY', payload: h })).catch(() => {})
    } catch (err) {
      dispatch({ type: 'SET_ERROR', payload: String(err) })
    } finally {
      dispatch({ type: 'SET_SEARCHING', payload: false })
    }
  }, [state.searchParams])

  const handleAddToCollection = useCallback(async (word: WordOut, collectionId: number) => {
    const metadata: Record<string, unknown> = {
      score: word.score,
      syllables: word.syllables_cmu ?? word.syllables,
      frequency: word.frequency,
      defs: word.defs,
      stress_pattern: word.stress_pattern,
      tags: word.tags,
    }
    try {
      await api.addWordToCollection(collectionId, word.word, metadata)
      api.getCollections().then((c) => dispatch({ type: 'SET_COLLECTIONS', payload: c })).catch(() => {})
    } catch {
      // word already in collection or other error - silently ignore
    }
  }, [])

  const handleCreateCollection = useCallback(async (name: string) => {
    const col = await api.createCollection(name)
    dispatch({ type: 'SET_COLLECTIONS', payload: [...state.collections, col] })
    dispatch({ type: 'SET_ACTIVE_COLLECTION', payload: col.id })
  }, [state.collections])

  const handleDeleteCollection = useCallback(async (id: number) => {
    await api.deleteCollection(id)
    api.getCollections().then((c) => dispatch({ type: 'SET_COLLECTIONS', payload: c })).catch(() => {})
    if (state.activeCollectionId === id) {
      dispatch({ type: 'SET_ACTIVE_COLLECTION', payload: null })
    }
  }, [state.activeCollectionId])

  const handleDeleteHistory = useCallback(async (id: number) => {
    await api.deleteHistoryEntry(id)
    dispatch({ type: 'SET_HISTORY', payload: state.history.filter((h) => h.id !== id) })
  }, [state.history])

  const handleReplaySearch = useCallback((query: Partial<SearchRequest>) => {
    const merged = { ...DEFAULT_SEARCH, ...query }
    dispatch({ type: 'SET_PARAMS', payload: merged })
    handleSearch(merged)
  }, [handleSearch])

  return (
    <div className="app-shell">
      <Header
        theme={state.theme}
        onToggleTheme={() => dispatch({ type: 'TOGGLE_THEME' })}
        onToggleCollections={() => dispatch({ type: 'TOGGLE_COLLECTIONS' })}
        collectionsOpen={state.collectionsOpen}
      />

      <div className="layout-body">
        <aside className="search-sidebar">
          <div className="search-sidebar-inner">
            <SearchPanel
              params={state.searchParams}
              onChange={(p) => dispatch({ type: 'SET_PARAMS', payload: p })}
              onSearch={() => handleSearch()}
              isSearching={state.isSearching}
            />
          </div>
        </aside>

        <main className="results-main">
          <div className="results-scroll">
            <ResultsArea
              results={state.results}
              isSearching={state.isSearching}
              error={state.searchError}
              sourcesRevealed={state.sourcesRevealed}
              onToggleSources={() => dispatch({ type: 'TOGGLE_SOURCES' })}
              collections={state.collections}
              activeCollectionId={state.activeCollectionId}
              onAddToCollection={handleAddToCollection}
              onSetActiveCollection={(id) => dispatch({ type: 'SET_ACTIVE_COLLECTION', payload: id })}
            />
          </div>

          <HistoryPanel
            history={state.history}
            open={state.historyOpen}
            onToggle={() => dispatch({ type: 'TOGGLE_HISTORY' })}
            onReplay={handleReplaySearch}
            onDelete={handleDeleteHistory}
          />
        </main>

        {state.collectionsOpen && (
          <aside className="collections-sidebar">
            <CollectionsSidebar
              collections={state.collections}
              activeCollectionId={state.activeCollectionId}
              onSetActive={(id) => dispatch({ type: 'SET_ACTIVE_COLLECTION', payload: id })}
              onCreate={handleCreateCollection}
              onDelete={handleDeleteCollection}
              onWordDropped={(word) => {
                if (state.activeCollectionId != null) {
                  handleAddToCollection(word, state.activeCollectionId)
                }
              }}
            />
          </aside>
        )}
      </div>
    </div>
  )
}
