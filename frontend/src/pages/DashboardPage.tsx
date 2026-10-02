import React, { useState } from 'react'
import { VacancyForm } from '../components/VacancyForm'
import { MetricCard } from '../components/MetricCard'
import type { VacancyResponse } from '../types'

function BuildingIcon() {
  return (
    <svg width={14} height={14} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 21V5a1 1 0 011-1h14a1 1 0 011 1v16M8 21h8m-4-8h.01M12 16h.01M8 13h.01M16 13h.01M8 17h.01M16 17h.01" />
    </svg>
  )
}

function MapPinIcon() {
  return (
    <svg width={14} height={14} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z" />
    </svg>
  )
}

function BriefcaseIcon() {
  return (
    <svg width={14} height={14} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M20 7l-8-4-8 4m16 0v10a2 2 0 01-2 2H6a2 2 0 01-2-2V7m16 0l-8 4m-8-4l8 4m0 0v10" />
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
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 3v18h18M7 16l4-8 4 4 4-6" />
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

export default function DashboardPage() {
  const [result, setResult] = useState<VacancyResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [hasResult, setHasResult] = useState(false)

  function handleResult(data: VacancyResponse) {
    setResult(data)
    setHasResult(true)
  }

  function ExternalLinkIcon() {
    return (
      <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" />
      </svg>
    )
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
              <div className="flex-between" style={{ alignItems: 'flex-start' }}>
                <div>
                  <h3>{result.title}</h3>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'monospace', marginTop: 2 }}>
                    ID: {result.id}
                  </div>
                </div>
                <div className="flex" style={{ gap: 8 }}>
                  <a
                    className="btn-icon"
                    title="Open details"
                    href={`/vacancies/${result.id}`}
                    style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(255,255,255,.04)', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', textDecoration: 'none' }}
                  >
                    <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </a>
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
  )
}