export interface WordOut {
  word: string
  score: number | null
  defs: string[]
  tags: string[]
  syllables: number | null
  frequency: number | null
  stress_pattern: string | null
  phonemes: string[] | null
  syllables_cmu: number | null
}

export interface SearchRequest {
  theme: string
  emotions: string[]
  topics: string
  spelling_pattern: string
  starts_with: string
  ends_with: string
  contains: string
  rhyme_with: string
  sounds_like: string
  max_results: number
  prefer_common: boolean
  pos_filter: string
  syllable_min: number | null
  syllable_max: number | null
  stress_pattern: string
  phonetic_match: string
  phonetic_anchor: string
}

export interface SearchResponse {
  bank_a: WordOut[]
  bank_b: WordOut[]
  bank_a_source: string
  bank_b_source: string
  info: string | null
  warnings: string[]
  search_id: number | null
}

export interface HistoryEntry {
  id: number
  query: Partial<SearchRequest>
  result_count: number
  created_at: string
}

export interface Collection {
  id: number
  name: string
  created_at: string
  word_count: number
}

export interface CollectionWord {
  word: string
  metadata: Record<string, unknown>
  added_at: string
}

export interface PhonemeData {
  word: string
  phonemes: string[] | null
  stress_pattern: string | null
  syllables: number | null
  assonance_vowels: string[]
  alliteration_onset: string[]
  consonance_consonants: string[]
  available: boolean
}

export type PosFilter = '' | 'n' | 'v' | 'adj' | 'adv'
export type PhoneticMode = 'none' | 'assonance' | 'alliteration' | 'consonance'

export const DEFAULT_SEARCH: SearchRequest = {
  theme: '',
  emotions: [],
  topics: '',
  spelling_pattern: '',
  starts_with: '',
  ends_with: '',
  contains: '',
  rhyme_with: '',
  sounds_like: '',
  max_results: 30,
  prefer_common: false,
  pos_filter: '',
  syllable_min: null,
  syllable_max: null,
  stress_pattern: '',
  phonetic_match: 'none',
  phonetic_anchor: '',
}
