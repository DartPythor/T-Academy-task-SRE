import React, { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { MetricCard } from '../components/MetricCard'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { getVacancy, deleteVacancy, recalculateVacancyMetrics } from '../api/client'
import type { VacancyResponse } from '../types'
import { VACANCY_STATUSES } from '../types'

function ArrowLeftIcon() {
  return (
    <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" d="M19 12H5m7 7l-7-7 7-7" />
    </svg>
  )
}

function StatusBadge({ status }: { status: string }) {
  const info = VACANCY_STATUSES.find(s => s.value === status)
  return (
    <span className="badge" style={{ backgroundColor: info?.color ?? '#6b7280', color: '#fff', fontSize: 13 }}>
      {info?.label ?? status}
    </span>
  )
}

export function VacancyDetailPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [vacancy, setVacancy] = useState<VacancyResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [recalculating, setRecalculating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)

  const load = useCallback(async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const data = await getVacancy(id)
      setVacancy(data)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { load() }, [load])

  async function handleDelete() {
    if (!id) return
    try {
      await deleteVacancy(id)
      navigate('/vacancies')
    } catch (err) {
      setError((err as Error).message)
      setShowDelete(false)
    }
  }

  async function handleRecalculate() {
    if (!id || !vacancy) return
    setRecalculating(true)
    setError(null)
    try {
      const salary = vacancy.metric
        ? {
            salary: {
              min_amount: vacancy.metric.salary_min ? { amount: vacancy.metric.salary_min.amount, currency: vacancy.metric.salary_min.currency } : null,
              max_amount: vacancy.metric.salary_max ? { amount: vacancy.metric.salary_max.amount, currency: vacancy.metric.salary_max.currency } : null,
              gross: null,
            },
          }
        : { salary: { min_amount: null, max_amount: null, gross: null } }
      const updated = await recalculateVacancyMetrics(id, salary)
      setVacancy(updated)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setRecalculating(false)
    }
  }

  if (loading) {
    return (
      <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
        <div className="skeleton-text" style={{ height: 24, width: 300, marginBottom: 24 }} />
        <div className="skeleton-text" style={{ height: 400 }} />
      </main>
    )
  }

  if (error && !vacancy) {
    return (
      <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
        <div className="error-banner">{error}</div>
        <button className="btn-secondary" onClick={() => navigate('/vacancies')} style={{ marginTop: 16 }}>
          <ArrowLeftIcon /> Back to vacancies
        </button>
      </main>
    )
  }

  if (!vacancy) return null

  const metric = vacancy.metric
  const scamScore = metric?.scam_score ?? 0
  const applyScore = metric?.apply_score ?? 0
  const confidence = metric ? Math.round(metric.confidence * 100) : 0
  const scamColor = scamScore >= 70 ? 'red' : scamScore >= 40 ? 'amber' : 'emerald'
  const applyColor = applyScore >= 70 ? 'emerald' : applyScore >= 40 ? 'amber' : 'red'

  return (
    <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
      {/* Back button */}
      <button className="btn-secondary" onClick={() => navigate('/vacancies')} style={{ marginBottom: 24 }}>
        <ArrowLeftIcon /> Назад к вакансиям
      </button>

      {error && <div className="error-banner animate-fade-in">{error}</div>}

      {/* Header */}
      <div className="page-header" style={{ marginBottom: 24 }}>
        <div>
          <div className="flex" style={{ alignItems: 'center', gap: 12, marginBottom: 4 }}>
            <h2 style={{ margin: 0 }}>{vacancy.title}</h2>
            <StatusBadge status={vacancy.status} />
          </div>
          <p className="text-muted">
            {[vacancy.company_name, vacancy.location, vacancy.employment_type?.replace('_', ' '), vacancy.work_mode]
              .filter(Boolean)
              .join(' · ')}
          </p>
        </div>
        <div className="flex" style={{ gap: 8 }}>
          <button
            className="btn-primary"
            onClick={handleRecalculate}
            disabled={recalculating}
          >
            {recalculating ? 'Пересчёт...' : 'Пересчитать метрики'}
          </button>
          <button className="btn-secondary" onClick={() => navigate(`/vacancies/${id}/edit`)}>
            Редактировать
          </button>
          <button className="btn-danger" onClick={() => setShowDelete(true)}>
            Удалить
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Main info */}
        <div className="glass" style={{ padding: 24 }}>
          <h3 className="form-section-header" style={{ marginBottom: 16 }}>Основная информация</h3>
          <div className="detail-grid">
            <div className="detail-field">
              <span className="detail-label">ID</span>
              <span className="detail-value mono">{vacancy.id}</span>
            </div>
            <div className="detail-field">
              <span className="detail-label">Source ID</span>
              <span className="detail-value mono">{vacancy.source_id}</span>
            </div>
            <div className="detail-field">
              <span className="detail-label">External ID</span>
              <span className="detail-value mono">{vacancy.external_id}</span>
            </div>
            <div className="detail-field">
              <span className="detail-label">URL</span>
              <a href={vacancy.url} target="_blank" rel="noopener noreferrer" className="table-link">{vacancy.url}</a>
            </div>
            {vacancy.description && (
              <div className="detail-field" style={{ gridColumn: '1 / -1' }}>
                <span className="detail-label">Description</span>
                <p className="detail-value" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>{vacancy.description}</p>
              </div>
            )}
            <div className="detail-field">
              <span className="detail-label">Created</span>
              <span className="detail-value">{new Date(vacancy.created_at).toLocaleString()}</span>
            </div>
            <div className="detail-field">
              <span className="detail-label">Updated</span>
              <span className="detail-value">{new Date(vacancy.updated_at).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Skills */}
        {vacancy.skills.length > 0 && (
          <div className="glass" style={{ padding: 24 }}>
            <h3 className="form-section-header" style={{ marginBottom: 12 }}>Навыки</h3>
            <div className="flex" style={{ flexWrap: 'wrap', gap: 6 }}>
              {vacancy.skills.map(s => (
                <span key={s.id} className="skill-tag">{s.name}</span>
              ))}
            </div>
          </div>
        )}

        {/* Metrics */}
        {metric && (
          <>
            <div className="glass" style={{ padding: 24 }}>
              <h3 className="form-section-header" style={{ marginBottom: 16 }}>Метрики</h3>
              <div className="metric-grid">
                <MetricCard
                  title="SCAM SCORE"
                  value={scamScore}
                  max={100}
                  color={scamColor}
                  isLoading={false}
                  subtitle={
                    scamScore >= 70 ? 'Высокий риск' :
                    scamScore >= 40 ? 'Средний риск' : 'Низкий риск'
                  }
                />
                <MetricCard
                  title="APPLY SCORE"
                  value={applyScore}
                  max={100}
                  color={applyColor}
                  isLoading={false}
                  subtitle={
                    applyScore >= 70 ? 'Стоит откликнуться' :
                    applyScore >= 40 ? 'Возможно' : 'Лучше пропустить'
                  }
                />
              </div>
              <div style={{ marginTop: 16 }}>
                <span className="detail-label">Уверенность: <strong>{confidence}%</strong></span>
                {metric.calculated_at && (
                  <span className="text-muted" style={{ marginLeft: 16, fontSize: 12 }}>
                    Рассчитано: {new Date(metric.calculated_at).toLocaleString()}
                  </span>
                )}
              </div>
            </div>

            {/* Salary */}
            {(metric.salary_min || metric.salary_max) && (
              <div className="glass" style={{ padding: 24 }}>
                <h3 className="form-section-header" style={{ marginBottom: 12 }}>Зарплата</h3>
                <div className="salary-amount" style={{ fontSize: 18 }}>
                  {metric.salary_min && `${metric.salary_min.amount.toLocaleString()} ${metric.salary_min.currency}`}
                  {metric.salary_min && metric.salary_max && ' — '}
                  {metric.salary_max && `${metric.salary_max.amount.toLocaleString()} ${metric.salary_max.currency}`}
                </div>
              </div>
            )}
          </>
        )}

        {!metric && (
          <div className="glass" style={{ padding: 24, textAlign: 'center' }}>
            <p className="text-muted">Метрики ещё не рассчитаны. Нажмите "Пересчитать метрики".</p>
          </div>
        )}
      </div>

      <ConfirmDialog
        isOpen={showDelete}
        title="Удалить вакансию"
        message="Вы уверены? Вакансия и все метрики будут удалены безвозвратно."
        onConfirm={handleDelete}
        onCancel={() => setShowDelete(false)}
      />
    </main>
  )
}