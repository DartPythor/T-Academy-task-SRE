import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCompany } from '../api/client'

export function CompanyFormPage() {
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [website, setWebsite] = useState('')
  const [description, setDescription] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) { setError('Name is required'); return }

    setSaving(true)
    setError(null)
    try {
      await createCompany({
        name,
        website: website.trim() || null,
        description: description.trim() || null,
      })
      navigate('/companies')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
      <div className="page-header">
        <div>
          <h2>Новая компания</h2>
          <p className="text-muted">Добавьте компанию-работодателя</p>
        </div>
      </div>

      {error && <div className="error-banner animate-fade-in">{error}</div>}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 32, maxWidth: 640 }}>
        <div className="glass" style={{ padding: 24 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label>Название <span className="required">*</span></label>
              <input
                placeholder="Яндекс"
                value={name}
                onChange={e => { setName(e.target.value); setError(null) }}
              />
            </div>
            <div>
              <label>Веб-сайт</label>
              <input
                placeholder="https://yandex.ru"
                value={website}
                onChange={e => setWebsite(e.target.value)}
              />
            </div>
            <div>
              <label>Описание</label>
              <textarea
                placeholder="Описание компании..."
                value={description}
                onChange={e => setDescription(e.target.value)}
                rows={4}
              />
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={() => navigate('/companies')}>
            Отмена
          </button>
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? 'Сохранение...' : 'Создать'}
          </button>
        </div>
      </form>
    </main>
  )
}