import React, { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createVacancy, getVacancy, updateVacancy, listSources } from '../api/client'
import type { Money, SalaryRange, SourceResponse, VacancyCreateRequest, VacancyUpdateRequest } from '../types'
import { EMPLOYMENT_TYPES, WORK_MODES, CURRENCIES } from '../types'

interface FormState {
  title: string
  url: string
  source_id: string
  company_name: string
  location: string
  description: string
  employment_type: string
  work_mode: string
  salary_min: string
  salary_max: string
  salary_currency: string
  salary_gross: boolean
  skill_names: string
}

const emptyForm: FormState = {
  title: '', url: '', source_id: '', company_name: '', location: '', description: '',
  employment_type: '', work_mode: '',
  salary_min: '', salary_max: '', salary_currency: 'RUB',
  salary_gross: false, skill_names: '',
}

export function VacancyFormPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEdit = Boolean(id)

  const [form, setForm] = useState<FormState>(emptyForm)
  const [sources, setSources] = useState<SourceResponse[]>([])
  const [loading, setLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load sources for dropdown
  useEffect(() => {
    listSources(true)
      .then(setSources)
      .catch(() => { /* non-critical */ })
  }, [])

  // Load vacancy data for edit
  useEffect(() => {
    if (!id) return
    getVacancy(id)
      .then(v => {
        setForm({
          title: v.title,
          url: v.url,
          source_id: v.source_id,
          company_name: v.company_name ?? '',
          location: v.location ?? '',
          description: v.description,
          employment_type: v.employment_type ?? '',
          work_mode: v.work_mode ?? '',
          salary_min: v.metric?.salary_min?.amount?.toString() ?? '',
          salary_max: v.metric?.salary_max?.amount?.toString() ?? '',
          salary_currency: v.metric?.salary_min?.currency ?? 'RUB',
          salary_gross: false,
          skill_names: v.skills.map(s => s.name).join(', '),
        })
      })
      .catch(err => setError((err as Error).message))
      .finally(() => setLoading(false))
  }, [id])

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm(prev => ({ ...prev, [key]: value }))
    setError(null)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.title.trim()) { setError('Название вакансии обязательно'); return }
    if (!form.url.trim()) { setError('URL вакансии обязателен'); return }
    if (!isEdit && !form.source_id) { setError('Необходимо выбрать источник'); return }

    setSaving(true)
    setError(null)

    try {
      if (isEdit && id) {
        const payload: VacancyUpdateRequest = {
          title: form.title,
          url: form.url,
          description: form.description || null,
          location: form.location || null,
          employment_type: form.employment_type || null,
          work_mode: form.work_mode || null,
          skill_names: form.skill_names.split(',').map(s => s.trim()).filter(Boolean),
        }
        await updateVacancy(id, payload)
        navigate(`/vacancies/${id}`)
      } else {
        const minMoney: Money | null = form.salary_min.trim()
          ? { amount: parseFloat(form.salary_min), currency: form.salary_currency }
          : null
        const maxMoney: Money | null = form.salary_max.trim()
          ? { amount: parseFloat(form.salary_max), currency: form.salary_currency }
          : null
        const salary: SalaryRange = { min_amount: minMoney, max_amount: maxMoney, gross: form.salary_gross || null }
        const skillNames = form.skill_names.split(',').map(s => s.trim()).filter(Boolean)

        const payload: VacancyCreateRequest = {
          source_id: form.source_id,
          external_id: crypto.randomUUID(),
          title: form.title,
          url: form.url,
          salary,
          description: form.description,
          company_name: form.company_name || null,
          location: form.location || null,
          employment_type: (form.employment_type || null) as VacancyCreateRequest['employment_type'],
          work_mode: (form.work_mode || null) as VacancyCreateRequest['work_mode'],
          skill_names: skillNames.length > 0 ? skillNames : null,
        }
        await createVacancy(payload)
        navigate('/vacancies')
      }
    } catch (err) {
      setError((err as { message?: string })?.message || 'Ошибка при сохранении')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
        <div className="skeleton-text" style={{ height: 24, width: 200, marginBottom: 24 }} />
        <div className="skeleton-text" style={{ height: 400 }} />
      </main>
    )
  }

  return (
    <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
      <div className="page-header">
        <div>
          <h2>{isEdit ? 'Редактировать вакансию' : 'Новая вакансия'}</h2>
          <p className="text-muted">{isEdit ? 'Измените данные вакансии' : 'Добавьте новую вакансию в систему'}</p>
        </div>
      </div>

      {error && <div className="error-banner animate-fade-in">{error}</div>}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 32, maxWidth: 800 }}>
        {/* Source */}
        {!isEdit && (
          <div className="glass" style={{ padding: 24 }}>
            <div className="form-section-header">
              <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Источник
            </div>
            <div style={{ marginTop: 12 }}>
              <label>Источник вакансии <span className="required">*</span></label>
              <select value={form.source_id} onChange={e => update('source_id', e.target.value)}>
                <option value="">Выберите источник</option>
                {sources.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.type})
                  </option>
                ))}
              </select>
              {sources.length === 0 && (
                <p className="text-muted" style={{ fontSize: 12, marginTop: 4 }}>
                  Нет доступных источников. Сначала создайте источник в разделе Sources.
                </p>
              )}
            </div>
          </div>
        )}

        {/* Main info */}
        <div className="glass" style={{ padding: 24 }}>
          <div className="form-section-header">
            <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Основная информация
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 12 }}>
            <div>
              <label>Название вакансии <span className="required">*</span></label>
              <input
                placeholder="Senior Python Developer"
                value={form.title}
                onChange={e => update('title', e.target.value)}
              />
            </div>

            <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(2, 1fr)' }}>
              <div>
                <label>URL вакансии <span className="required">*</span></label>
                <input placeholder="https://hh.ru/vacancy/123" value={form.url} onChange={e => update('url', e.target.value)} />
              </div>
              <div>
                <label>Компания</label>
                <input placeholder="Яндекс" value={form.company_name} onChange={e => update('company_name', e.target.value)} />
              </div>
              <div>
                <label>Локация</label>
                <input placeholder="Москва / Remote" value={form.location} onChange={e => update('location', e.target.value)} />
              </div>
              <div>
                <label>Тип занятости</label>
                <select value={form.employment_type} onChange={e => update('employment_type', e.target.value)}>
                  <option value="">Не указано</option>
                  {EMPLOYMENT_TYPES.map(t => (<option key={t.value} value={t.value}>{t.label}</option>))}
                </select>
              </div>
            </div>

            <div>
              <label>Формат работы</label>
              <div className="chip-group">
                {WORK_MODES.map(m => (
                  <button
                    key={m.value}
                    type="button"
                    onClick={() => update('work_mode', form.work_mode === m.value ? '' : m.value)}
                    className={`chip ${form.work_mode === m.value ? 'active' : ''}`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Salary */}
        <div className="glass" style={{ padding: 24 }}>
          <div className="form-section-header">
            <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Зарплата
          </div>

          <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(4, 1fr)', marginTop: 12 }}>
            <div>
              <label>От</label>
              <input type="number" min={0} placeholder="100000" value={form.salary_min} onChange={e => update('salary_min', e.target.value)} />
            </div>
            <div>
              <label>До</label>
              <input type="number" min={0} placeholder="250000" value={form.salary_max} onChange={e => update('salary_max', e.target.value)} />
            </div>
            <div>
              <label>Валюта</label>
              <select value={form.salary_currency} onChange={e => update('salary_currency', e.target.value)}>
                {CURRENCIES.map(c => (<option key={c.value} value={c.value}>{c.label}</option>))}
              </select>
            </div>
            <div>
              <label>Gross / Net</label>
              <div className="gross-toggle">
                <button type="button" onClick={() => update('salary_gross', !form.salary_gross)}
                  className={`gross-btn ${form.salary_gross ? 'active' : ''}`}>
                  {form.salary_gross ? 'Gross' : 'Net / Не указано'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Description & Skills */}
        <div className="glass" style={{ padding: 24 }}>
          <div className="form-section-header">
            <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h7" />
            </svg>
            Описание и навыки
          </div>

          <div style={{ marginTop: 12 }}>
            <label>Описание</label>
            <textarea placeholder="Обязанности, требования, условия..." value={form.description} onChange={e => update('description', e.target.value)} />
          </div>

          <div style={{ marginTop: 16 }}>
            <label>Навыки (через запятую)</label>
            <input placeholder="Python, Django, PostgreSQL, Docker" value={form.skill_names} onChange={e => update('skill_names', e.target.value)} />
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={() => navigate(isEdit ? `/vacancies/${id}` : '/vacancies')}>
            Отмена
          </button>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? 'Сохранение...' : isEdit ? 'Сохранить' : 'Создать'}
          </button>
        </div>
      </form>
    </main>
  )
}