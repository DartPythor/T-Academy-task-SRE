import type {
  CompanyCreateRequest,
  CompanyResponse,
  Metric,
  PaginatedResponse,
  SourceCreateRequest,
  SourceResponse,
  SourceUpdateRequest,
  VacancyCreateRequest,
  VacancyResponse,
  VacancyUpdateRequest,
} from '../types'

const API_BASE = '/api/v1'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }

  if (res.status === 204) return undefined as T
  return res.json()
}

// ─── Vacancies ───────────────────────────────────────────────

export async function createVacancy(
  data: VacancyCreateRequest,
): Promise<VacancyResponse> {
  return request('/vacancies', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getVacancy(id: string): Promise<VacancyResponse> {
  return request(`/vacancies/${id}`)
}

export async function listVacancies(
  params?: { status?: string; limit?: number; offset?: number },
): Promise<PaginatedResponse<VacancyResponse>> {
  const qs = new URLSearchParams()
  if (params?.status) qs.set('status', params.status)
  if (params?.limit) qs.set('limit', String(params.limit))
  if (params?.offset) qs.set('offset', String(params.offset))
  const query = qs.toString()
  return request(`/vacancies${query ? `?${query}` : ''}`)
}

export async function updateVacancy(
  id: string,
  data: VacancyUpdateRequest,
): Promise<VacancyResponse> {
  return request(`/vacancies/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteVacancy(id: string): Promise<void> {
  return request(`/vacancies/${id}`, { method: 'DELETE' })
}

export async function getVacancyMetrics(id: string): Promise<Metric> {
  return request(`/vacancies/${id}/metrics`)
}

export async function recalculateVacancyMetrics(
  id: string,
  salary: { salary: { min_amount?: { amount: number; currency: string } | null; max_amount?: { amount: number; currency: string } | null; gross?: boolean | null } },
): Promise<VacancyResponse> {
  return request(`/vacancies/${id}/recalculate`, {
    method: 'POST',
    body: JSON.stringify(salary),
  })
}

// ─── Sources ─────────────────────────────────────────────────

export async function listSources(
  enabledOnly = false,
): Promise<SourceResponse[]> {
  const qs = enabledOnly ? '?enabled_only=true' : ''
  return request(`/sources${qs}`)
}

export async function getSource(id: string): Promise<SourceResponse> {
  return request(`/sources/${id}`)
}

export async function createSource(
  data: SourceCreateRequest,
): Promise<SourceResponse> {
  return request('/sources', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateSource(
  id: string,
  data: SourceUpdateRequest,
): Promise<SourceResponse> {
  return request(`/sources/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteSource(id: string): Promise<void> {
  return request(`/sources/${id}`, { method: 'DELETE' })
}

// ─── Companies ───────────────────────────────────────────────

export async function listCompanies(): Promise<CompanyResponse[]> {
  return request('/companies')
}

export async function getCompany(id: string): Promise<CompanyResponse> {
  return request(`/companies/${id}`)
}

export async function createCompany(
  data: CompanyCreateRequest,
): Promise<CompanyResponse> {
  return request('/companies', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

// ─── Health ──────────────────────────────────────────────────

export async function healthCheck(): Promise<{ status: string }> {
  return request('/health')
}