import React, { useState } from 'react'
import type { VacancyCreateRequest, SalaryRange, Money } from '../types'
import { EMPLOYMENT_TYPES, WORK_MODES, CURRENCIES, generateId } from '../types'
import type { VacancyResponse } from '../types'
import { createVacancy } from '../api/client'

interface VacancyFormProps {
  onResult: (result: VacancyResponse) => void
  onLoading: (loading: boolean) => void
}

interface FormState {
  title: string
  url: string
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
  title: '', url: '', company_name: '', location: '', description: '',
  employment_type: '', work_mode: '',
  salary_min: '', salary_max: '', salary_currency: 'RUB',
  salary_gross: false, skill_names: '',
}

export function VacancyForm({ onResult, onLoading }: VacancyFormProps) {
  const [form, setForm] = useState<FormState>(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm(prev => ({ ...prev, [key]: value }))
    setError(null)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.title.trim()) { setError('Название вакансии обязательно'); return }
    if (!form.url.trim()) { setError('URL вакансии обязателен'); return }

    setSubmitting(true)
    onLoading(true)
    setError(null)

    const minMoney: Money | null = form.salary_min.trim()
      ? { amount: parseFloat(form.salary_min), currency: form.salary_currency }
      : null
    const maxMoney: Money | null = form.salary_max.trim()
      ? { amount: parseFloat(form.salary_max), currency: form.salary_currency }
      : null

    const salary: SalaryRange = { min_amount: minMoney, max_amount: maxMoney, gross: form.salary_gross || null }
    const skillNames = form.skill_names.split(',').map(s => s.trim()).filter(Boolean)

    const payload: VacancyCreateRequest = {
      source_id: generateId(),
      external_id: generateId(),
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

    try {
      const result = await createVacancy(payload)
      onResult(result)
    } catch (err) {
      setError((err as { message?: string })?.message || 'Ошибка при создании вакансии')
    } finally {
      setSubmitting(false)
      onLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* ▸ Основная информация */}
      <div className="glass" style={{ padding: 24 }}>
        <div className="form-section-header">
          <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Основная информация
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
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

      {/* ▸ Зарплата */}
      <div className="glass" style={{ padding: 24 }}>
        <div className="form-section-header">
          <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Зарплата
        </div>

        <div style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(4, 1fr)' }}>
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

      {/* ▸ Описание и навыки */}
      <div className="glass" style={{ padding: 24 }}>
        <div className="form-section-header">
          <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h7" />
          </svg>
          Описание и навыки
        </div>

        <div>
          <label>Описание</label>
          <textarea placeholder="Обязанности, требования, условия..." value={form.description} onChange={e => update('description', e.target.value)} />
        </div>

        <div style={{ marginTop: 16 }}>
          <label>Навыки (через запятую)</label>
          <input placeholder="Python, Django, PostgreSQL, Docker" value={form.skill_names} onChange={e => update('skill_names', e.target.value)} />
        </div>
      </div>

      {error && <div className="error-banner animate-fade-in">{error}</div>}

      <button type="submit" disabled={submitting} className="btn-primary">
        <svg width={18} height={18} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" d="M12 2v4m-3.1 9l2.1 7m3.1-9h-2.1m-1 0v6M15 12l-10-5 5 6-5-5h11" />
        </svg>
        {submitting ? 'Анализируем...' : 'Анализировать вакансию'}
      </button>
    </form>
  )
}