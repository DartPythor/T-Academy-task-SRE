import React, { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { DataTable, type Column } from '../components/DataTable'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { listSources, deleteSource } from '../api/client'
import type { SourceResponse, SourceType } from '../types'
import { SOURCE_TYPES } from '../types'

function SourceTypeBadge({ type }: { type: SourceType }) {
  const info = SOURCE_TYPES.find(s => s.value === type)
  return (
    <span
      className="badge"
      style={{ backgroundColor: info?.color ?? '#6b7280', color: '#fff' }}
    >
      {info?.label ?? type}
    </span>
  )
}

export function SourceListPage() {
  const navigate = useNavigate()
  const [sources, setSources] = useState<SourceResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listSources()
      setSources(data)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleDelete() {
    if (!deleteId) return
    try {
      await deleteSource(deleteId)
      setDeleteId(null)
      await load()
    } catch (err) {
      setError((err as Error).message)
      setDeleteId(null)
    }
  }

  const columns: Column<SourceResponse>[] = [
    {
      key: 'name',
      label: 'Name',
      render: s => <strong>{s.name}</strong>,
    },
    {
      key: 'type',
      label: 'Type',
      render: s => <SourceTypeBadge type={s.type} />,
    },
    {
      key: 'url',
      label: 'URL',
      render: s => (
        <a href={s.url} target="_blank" rel="noopener noreferrer" className="table-link" onClick={e => e.stopPropagation()}>
          {s.url.length > 50 ? s.url.slice(0, 50) + '…' : s.url}
        </a>
      ),
    },
    {
      key: 'enabled',
      label: 'Enabled',
      render: s => (
        <span className={`status-dot ${s.enabled ? 'active' : 'inactive'}`}>
          {s.enabled ? 'Yes' : 'No'}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      render: s => new Date(s.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: '',
      render: s => (
        <div className="table-actions" onClick={e => e.stopPropagation()}>
          <button className="btn-icon" title="Edit" onClick={() => navigate(`/sources/${s.id}/edit`)}>
            <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button className="btn-icon btn-icon-danger" title="Delete" onClick={() => setDeleteId(s.id)}>
            <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      ),
    },
  ]

  return (
    <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
      <div className="page-header">
        <div>
          <h2>Sources</h2>
          <p className="text-muted">Управление источниками вакансий</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/sources/new')}>
          <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" d="M12 4v16m8-8H4" />
          </svg>
          Добавить источник
        </button>
      </div>

      {error && <div className="error-banner animate-fade-in">{error}</div>}

      <div className="glass" style={{ padding: 0, overflow: 'hidden' }}>
        <DataTable
          columns={columns}
          data={sources}
          keyExtractor={s => s.id}
          isLoading={loading}
          emptyMessage="Нет источников. Создайте первый источник."
        />
      </div>

      <ConfirmDialog
        isOpen={deleteId !== null}
        title="Удалить источник"
        message="Вы уверены? Источник будет удалён без возможности восстановления."
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
      />
    </main>
  )
}