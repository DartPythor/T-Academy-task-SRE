import { useState } from 'react'
import { Header } from './components/Header'
import { VacancyForm } from './components/VacancyForm'
import { MetricCard } from './components/MetricCard'
import type { VacancyResponse } from './types'

function ExternalLinkIcon() {
  return (
    <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" />
    </svg>
  )
}

function BuildingIcon() {
  return (
    <svg width={14} height={14} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h7" />
    </svg>
  )
}

function MapPinIcon() {
  return (
    <svg width={14} height={14} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" d="M12 11h-1v-3h.01m8 12a4 4 0 01-3-3 3-3 1-2 0 2-1 0 2z" />
    </svg>
  )
}

function BriefcaseIcon() {
  return (
    <svg width={14} height={14} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 6h5M8 12h8M20 18h-9" />
    </svg>
  )
}

function RefreshIcon() {
  return (
    <svg width={14} height={14} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" d="M1 4v6h6M23 20v-6h-6" />
      <path strokeLinecap="round" d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15" />
    </svg>
  )
}

function ChartIcon() {
  return (
    <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" d="M18 20V10M12 20V4M6 20v-6" />
    </svg>
  )
}

function SalaryIcon() {
  return (
    <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
}

export default function App() {
  const [result, setResult] = useState<VacancyResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [hasResult, setHasResult] = useState(false)

  function handleResult(data: VacancyResponse) {
    setResult(data)
    setHasResult(true)
  }

  const metric = result?.metric
  const scamScore = metric?.scam_score ?? 0
  const applyScore = metric?.apply_score ?? 0
  const confidence = metric ? Math.round(metric.confidence * 100) : 0
  const salaryMin = metric?.salary_min
  const salaryMax = metric?.salary_max

  function verdictLabel(score: number): string {
    if (score >= 70) return 'apply'
    if (score >= 40) return 'maybe'
    return 'skip'
  }

  function verdictText(score: number): string {
    if (score >= 70) return 'APPLY'
    if (score >= 40) return 'MAYBE'
    return 'SKIP'
  }

  const scamColor = scamScore >= 70 ? 'red' : scamScore >= 40 ? 'amber' : 'emerald'
  const applyColor = applyScore >= 70 ? 'emerald' : applyScore >= 40 ? 'amber' : 'red'

  return (
    <>
      <div className="background-blobs">
        <div className="blob blob-1" />
        <div className="blob blob-2" />
      </div>

      <Header />

      <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
        <div className="grid-2">
          {/* Form */}
          <div>
            <div className="section-title">
              <h2>Новый анализ</h2>
              <p>Заполните данные о вакансии — мы рассчитаем метрики</p>
            </div>
            <VacancyForm onResult={handleResult} onLoading={setLoading} />
          </div>

          {/* Results */}
          {hasResult && result && (
            <div className="result-panel animate-fade-in">
              <div className="results-header">
                <h2 className="text-2xl font-bold">Результаты</h2>
                <button
                  onClick={() => { setResult(null); setHasResult(false) }}
                  className="new-analysis-btn"
                >
                  <RefreshIcon />
                  Новый анализ
                </button>
              </div>

              {/* Vacancy info */}
              <div className="glass vacancy-info animate-slide-up">
                <div className="flex-between">
                  <h3>{result.title}</h3>
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: 'rgba(255,255,255,.04)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: 'var(--text-muted)', flexShrink: 0,
                    }}
                  >
                    <ExternalLinkIcon />
                  </a>
                </div>

                <div className="vacancy-meta" style={{ marginTop: 8 }}>
                  {result.company_name && (
                    <span><BuildingIcon /> {result.company_name}</span>
                  )}
                  {result.location && (
                    <span><MapPinIcon /> {result.location}</span>
                  )}
                  {result.employment_type && (
                    <span><BriefcaseIcon /> {result.employment_type.replace('_', ' ')}</span>
                  )}
                  {result.work_mode && (
                    <span className="capitalize">{result.work_mode}</span>
                  )}
                </div>

                {result.skills.length > 0 && (
                  <div className="flex" style={{ flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                    {result.skills.map(s => (
                      <span key={s.id} className="skill-tag">{s.name}</span>
                    ))}
                  </div>
                )}
              </div>

              {/* Metric cards */}
              <div className="metric-grid" style={{ marginTop: 16 }}>
                <MetricCard
                  title="SCAM SCORE"
                  value={scamScore}
                  max={100}
                  color={scamColor}
                  isLoading={loading}
                  subtitle={
                    scamScore >= 70 ? 'Высокий риск — осторожно' :
                    scamScore >= 40 ? 'Средний риск' : 'Низкий риск'
                  }
                />
                <MetricCard
                  title="APPLY SCORE"
                  value={applyScore}
                  max={100}
                  color={applyColor}
                  isLoading={loading}
                  subtitle={
                    applyScore >= 70 ? 'Стоит откликнуться' :
                    applyScore >= 40 ? 'Возможно' : 'Лучше пропустить'
                  }
                />
              </div>

              {/* Confidence & Verdict */}
              <div className="glass result-section animate-slide-up">
                <div className="result-section-header">
                  <ChartIcon />
                  Уверенность прогноза
                </div>

                <div className="confidence-ring">
                  <div className="ring-chart">
                    <svg viewBox="0 0 36 36">
                      <circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(255,255,255,.05)" strokeWidth={3} />
                      <circle
                        cx="18" cy="18" r="15.5"
                        fill="none"
                        stroke="#818cf8"
                        strokeWidth={3}
                        strokeLinecap="round"
                        strokeDasharray={`${confidence * 0.97} ${100 - confidence * 0.97}`}
                        style={{ transition: 'stroke-dasharray 1s ease' }}
                      />
                    </svg>
                    <span className="ring-value">{confidence}%</span>
                  </div>

                  <div className="ring-info">
                    <div className="flex" style={{ alignItems: 'center', gap: 12, marginBottom: 4 }}>
                      <span className="text-xs text-muted">Вердикт:</span>
                      {metric && (
                        <span className={`verdict verdict-${verdictLabel(applyScore)}`}>
                          <span className="dot" />
                          {verdictText(applyScore)}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted">
                      {scamScore >= 70
                        ? '⚠️ Вакансия выглядит подозрительно. Будьте внимательны.'
                        : confidence >= 60
                          ? 'Достаточно данных для уверенного прогноза.'
                          : 'Мало данных — прогноз может быть неточным.'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Salary */}
              {(salaryMin || salaryMax) && (
                <div className="glass result-section salary-display animate-slide-up">
                  <div className="result-section-header">
                    <SalaryIcon />
                    Зарплатная вилка
                  </div>
                  <div className="salary-amount">
                    {salaryMin && `${salaryMin.amount.toLocaleString()} ${salaryMin.currency}`}
                    {salaryMin && salaryMax && ' — '}
                    {salaryMax && `${salaryMax.amount.toLocaleString()} ${salaryMax.currency}`}
                  </div>
                  {metric?.salary_gross !== null && metric?.salary_gross !== undefined && (
                    <div className="text-xs text-muted" style={{ marginTop: 4 }}>
                      {metric.salary_gross ? 'Gross (до вычета налогов)' : 'Net / не указано'}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  )
}