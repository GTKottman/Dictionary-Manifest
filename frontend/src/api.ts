import type {
  Collection,
  CollectionWord,
  HistoryEntry,
  PhonemeData,
  SearchRequest,
  SearchResponse,
} from './types'

const BASE = '/api'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? res.statusText)
  }
  return res.json()
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? res.statusText)
  }
  return res.json()
}

async function del(path: string): Promise<void> {
  const res = await fetch(`${BASE}${path}`, { method: 'DELETE' })
  if (!res.ok && res.status !== 204) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? res.statusText)
  }
}

async function patch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? res.statusText)
  }
  return res.json()
}

// Search
export const search = (req: SearchRequest): Promise<SearchResponse> =>
  post<SearchResponse>('/search', req)

// History
export const getHistory = (limit = 50): Promise<HistoryEntry[]> =>
  get<HistoryEntry[]>(`/history?limit=${limit}`)

export const deleteHistoryEntry = (id: number): Promise<void> =>
  del(`/history/${id}`)

export const clearHistory = (): Promise<void> => del('/history')

// Collections
export const getCollections = (): Promise<Collection[]> =>
  get<Collection[]>('/collections')

export const createCollection = (name: string): Promise<Collection> =>
  post<Collection>('/collections', { name })

export const renameCollection = (id: number, name: string): Promise<Collection> =>
  patch<Collection>(`/collections/${id}`, { name })

export const deleteCollection = (id: number): Promise<void> =>
  del(`/collections/${id}`)

export const getCollectionWords = (id: number): Promise<CollectionWord[]> =>
  get<CollectionWord[]>(`/collections/${id}/words`)

export const addWordToCollection = (
  collectionId: number,
  word: string,
  metadata: Record<string, unknown>
): Promise<{ word: string }> =>
  post<{ word: string }>(`/collections/${collectionId}/words`, { word, metadata })

export const removeWordFromCollection = (collectionId: number, word: string): Promise<void> =>
  del(`/collections/${collectionId}/words/${encodeURIComponent(word)}`)

export const exportCollection = (id: number, fmt: 'text' | 'tsv' = 'text'): Promise<{ content: string; format: string }> =>
  get<{ content: string; format: string }>(`/collections/${id}/export?fmt=${fmt}`)

// Phonetics
export const getPhonetics = (word: string): Promise<PhonemeData> =>
  get<PhonemeData>(`/phonetics/${encodeURIComponent(word)}`)
