const MOODS = [
  { id: 'melancholic', label: 'Melancholic', emoji: '🌧' },
  { id: 'dark', label: 'Dark', emoji: '🌑' },
  { id: 'haunting', label: 'Haunting', emoji: '👻' },
  { id: 'angry', label: 'Angry', emoji: '🔥' },
  { id: 'defiant', label: 'Defiant', emoji: '✊' },
  { id: 'rebellious', label: 'Rebellious', emoji: '⚡' },
  { id: 'fearful', label: 'Fearful', emoji: '😨' },
  { id: 'anxious', label: 'Anxious', emoji: '😰' },
  { id: 'lonely', label: 'Lonely', emoji: '🌫' },
  { id: 'nostalgic', label: 'Nostalgic', emoji: '📷' },
  { id: 'bittersweet', label: 'Bittersweet', emoji: '🥀' },
  { id: 'introspective', label: 'Introspective', emoji: '🔍' },
  { id: 'hopeful', label: 'Hopeful', emoji: '🌅' },
  { id: 'triumphant', label: 'Triumphant', emoji: '🏆' },
  { id: 'euphoric', label: 'Euphoric', emoji: '✨' },
  { id: 'romantic', label: 'Romantic', emoji: '❤' },
  { id: 'sensual', label: 'Sensual', emoji: '🌹' },
  { id: 'tender', label: 'Tender', emoji: '🕊' },
  { id: 'peaceful', label: 'Peaceful', emoji: '☁' },
  { id: 'ethereal', label: 'Ethereal', emoji: '🌙' },
  { id: 'spiritual', label: 'Spiritual', emoji: '🕯' },
  { id: 'mysterious', label: 'Mysterious', emoji: '🌀' },
  { id: 'powerful', label: 'Powerful', emoji: '💥' },
  { id: 'urgent', label: 'Urgent', emoji: '⏱' },
  { id: 'gritty', label: 'Gritty', emoji: '🏚' },
]

interface Props {
  selected: string[]
  onChange: (emotions: string[]) => void
}

export default function MoodPalette({ selected, onChange }: Props) {
  const toggle = (id: string) => {
    if (selected.includes(id)) {
      onChange(selected.filter((s) => s !== id))
    } else {
      onChange([...selected, id])
    }
  }

  return (
    <>
      <p style={{ fontSize: '0.78rem', color: 'var(--muted)', marginBottom: '0.4rem', lineHeight: 1.5 }}>
        Pick moods to layer emotional depth into your search. Stacks with your theme.
      </p>
      <div className="mood-palette">
        {MOODS.map((m) => (
          <button
            key={m.id}
            className={`mood-chip ${selected.includes(m.id) ? 'active' : ''}`}
            onClick={() => toggle(m.id)}
            title={m.label}
          >
            <span>{m.emoji}</span>
            {m.label}
          </button>
        ))}
      </div>
      {selected.length > 0 && (
        <button
          className="btn btn-ghost btn-sm"
          style={{ alignSelf: 'flex-start', paddingLeft: 0, marginTop: '0.2rem' }}
          onClick={() => onChange([])}
        >
          Clear moods
        </button>
      )}
    </>
  )
}
