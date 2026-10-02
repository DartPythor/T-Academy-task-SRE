import React, { useCallback, useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { DataTable, type Column } from '../components/DataTable'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { listVacancies, deleteVacancy } from '../api/client'
import type { VacancyResponse } from '../types'
import { VACANCY_STATUSES } from '../types'

function StatusBadge({ status }: { status: string }) {
  const info = VACANCY_STATUSES.find(s => s.value === status)
  return (
    <span
      className="badge"
      style={{ backgroundColor: info?.color ?? '#6b7280', color: '#fff' }}
    >
      {info?.label ?? status}
    </span>
  )
}

export function VacancyListPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [vacancies, setVacancies] = useState<VacancyResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  const statusFilter = searchParams.get('status') || ''

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: { status?: string; limit?: number; offset?: number } = { limit: 100 }
      if (statusFilter) params.status = statusFilter
      const data = await listVacancies(params)
      setVacancies(data.items)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => { load() }, [load])

  async function handleDelete() {
    if (!deleteId) return
    try {
      await deleteVacancy(deleteId)
      setDeleteId(null)
      await load()
    } catch (err) {
      setError((err as Error).message)
      setDeleteId(null)
    }
  }

  function toggleStatusFilter(value: string) {
    const next = statusFilter === value ? '' : value
    if (next) searchParams.set('status', next)
    else searchParams.delete('status')
    setSearchParams(searchParams)
  }

  const columns: Column<VacancyResponse>[] = [
    {
      key: 'title',
      label: 'Title',
      render: v => <strong>{v.title}</strong>,
    },
    {
      key: 'company_name',
      label: 'Company',
      render: v => v.company_name ?? <span className="text-muted">—</span>,
    },
    {
      key: 'location',
      label: 'Location',
      render: v => v.location ?? <span className="text-muted">—</span>,
    },
    {
      key: 'status',
      label: 'Status',
      render: v => <StatusBadge status={v.status} />,
    },
    {
      key: 'employment_type',
      label: 'Type',
      render: v => v.employment_type?.replace('_', ' ') ?? <span className="text-muted">—</span>,
    },
    {
      key: 'created_at',
      label: 'Created',
      render: v => new Date(v.created_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      label: '',
      render: v => (
        <div className="table-actions" onClick={e => e.stopPropagation()}>
          <button className="btn-icon" title="View" onClick={() => navigate(`/vacancies/${v.id}`)}>
            <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
          <button className="btn-icon" title="Edit" onClick={() => navigate(`/vacancies/${v.id}/edit`)}>
            <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button className="btn-icon btn-icon-danger" title="Delete" onClick={() => setDeleteId(v.id)}>
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
          <h2>Vacancies</h2>
          <p className="text-muted">Управление вакансиями</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/vacancies/new')}>
          <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" d="M12 4v16m8-8H4" />
          </svg>
          Новая вакансия
        </button>
      </div>

      {error && <div className="error-banner animate-fade-in">{error}</div>}

      {/* Status filter chips */}
      <div className="filter-chips" style={{ marginBottom: 16 }}>
        {VACANCY_STATUSES.map(s => (
          <button
            key={s.value}
            className={`chip ${statusFilter === s.value ? 'active' : ''}`}
            onClick={() => toggleStatusFilter(s.value)}
          >
            {s.label}
          </button>
        ))}
        {statusFilter && (
          <button className="chip chip-clear" onClick={() => setSearchParams({})}>
            ✕ Clear
          </button>
        )}
      </div>

      <div className="glass" style={{ padding: 0, overflow: 'hidden' }}>
        <DataTable
          columns={columns}
          data={vacancies}
          keyExtractor={v => v.id}
          isLoading={loading}
          emptyMessage="Нет вакансий."
          onRowClick={v => navigate(`/vacancies/${v.id}`)}
        />
      </div>

      <ConfirmDialog
        isOpen={deleteId !== null}
        title="Удалить вакансию"
        message="Вы уверены? Вакансия и все связанные метрики будут удалены."
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
      />
    </main>
  )
}