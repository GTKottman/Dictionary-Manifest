interface HeaderProps {
  theme: 'light' | 'dark'
  onToggleTheme: () => void
  onToggleCollections: () => void
  collectionsOpen: boolean
}

export default function Header({ theme, onToggleTheme, onToggleCollections, collectionsOpen }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-brand">
        <span>Lexicon</span>Shaper
      </div>
      <p className="header-tagline">Theme · Mood · Sound — word discovery for writers</p>

      <div className="header-actions">
        <button
          className="theme-toggle"
          onClick={onToggleTheme}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? '☀ Light' : '🌑 Dark'}
        </button>

        <button
          className="btn btn-secondary btn-sm"
          onClick={onToggleCollections}
          title={collectionsOpen ? 'Hide collections' : 'Show collections'}
        >
          {collectionsOpen ? '▶ Collections' : '◀ Collections'}
        </button>
      </div>
    </header>
  )
}
