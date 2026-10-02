import React, { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { DataTable, type Column } from '../components/DataTable'
import { listCompanies } from '../api/client'
import type { CompanyResponse } from '../types'

export function CompanyListPage() {
  const navigate = useNavigate()
  const [companies, setCompanies] = useState<CompanyResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listCompanies()
      setCompanies(data)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const columns: Column<CompanyResponse>[] = [
    {
      key: 'name',
      label: 'Name',
      render: c => <strong>{c.name}</strong>,
    },
    {
      key: 'website',
      label: 'Website',
      render: c => c.website ? (
        <a href={c.website} target="_blank" rel="noopener noreferrer" className="table-link" onClick={e => e.stopPropagation()}>
          {c.website}
        </a>
      ) : <span className="text-muted">—</span>,
    },
    {
      key: 'description',
      label: 'Description',
      render: c => c.description
        ? (c.description.length > 80 ? c.description.slice(0, 80) + '…' : c.description)
        : <span className="text-muted">—</span>,
    },
    {
      key: 'created_at',
      label: 'Created',
      render: c => new Date(c.created_at).toLocaleDateString(),
    },
  ]

  return (
    <main className="container" style={{ paddingTop: 40, paddingBottom: 40 }}>
      <div className="page-header">
        <div>
          <h2>Companies</h2>
          <p className="text-muted">Управление компаниями-работодателями</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/companies/new')}>
          <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" d="M12 4v16m8-8H4" />
          </svg>
          Добавить компанию
        </button>
      </div>

      {error && <div className="error-banner animate-fade-in">{error}</div>}

      <div className="glass" style={{ padding: 0, overflow: 'hidden' }}>
        <DataTable
          columns={columns}
          data={companies}
          keyExtractor={c => c.id}
          isLoading={loading}
          emptyMessage="Нет компаний. Создайте первую компанию."
        />
      </div>
    </main>
  )
}