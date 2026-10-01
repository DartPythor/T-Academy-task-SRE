export function Header() {
  return (
    <header>
      <div className="container">
        <div className="logo">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <h1 className="gradient-text" style={{ fontSize: 20 }}>Vacancy Analyzer</h1>
          <p className="text-xs text-muted">Анализ и метрики вакансий</p>
        </div>
      </div>
    </header>
  )
}