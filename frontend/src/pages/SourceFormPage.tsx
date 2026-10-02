import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createSource, getSource, updateSource } from '../api/client'
import type { SourceType } from '../types'
import { SOURCE_TYPES } from '../types'

export function SourceFormPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEdit = Boolean(id)

  const [name, setName] = useState('')
  const [type, setType] = useState<SourceType>('hh')
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    getSource(id)
      .then(s => {
        setName(s.name)
        setType(s.type)
        setUrl(s.url)
      })
      .catch(err => setError((err as Error).message))
      .finally(() => setLoading(false))
  }, [id])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) { setError('Name is required'); return }
    if (!url.trim()) { setError('URL is required'); return }

    setSaving(true)
    setError(null)
    try {
      if (isEdit && id) {
        await updateSource(id, { name, type, url })
      } else {
        await createSource({ name, type, url })
      }
      navigate('/sources')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
        <div className="skeleton-text" style={{ height: 24, width: 200, marginBottom: 24 }} />
        <div className="skeleton-text" style={{ height: 300 }} />
      </main>
    )
  }

  return (
    <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
      <div className="page-header">
        <div>
          <h2>{isEdit ? 'Редактировать источник' : 'Новый источник'}</h2>
          <p className="text-muted">{isEdit ? 'Измените данные источника' : 'Добавьте новый источник вакансий'}</p>
        </div>
      </div>

      {error && <div className="error-banner animate-fade-in">{error}</div>}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 32, maxWidth: 640 }}>
        <div className="glass" style={{ padding: 24 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label>Название <span className="required">*</span></label>
              <input
                placeholder="hh.ru"
                value={name}
                onChange={e => { setName(e.target.value); setError(null) }}
              />
            </div>
            <div>
              <label>Тип <span className="required">*</span></label>
              <select value={type} onChange={e => setType(e.target.value as SourceType)}>
                {SOURCE_TYPES.map(st => (
                  <option key={st.value} value={st.value}>{st.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label>URL <span className="required">*</span></label>
              <input
                placeholder="https://hh.ru"
                value={url}
                onChange={e => { setUrl(e.target.value); setError(null) }}
              />
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={() => navigate('/sources')}>
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