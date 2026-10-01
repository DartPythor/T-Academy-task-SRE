import type { VacancyCreateRequest, VacancyResponse } from '../types'

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

export async function healthCheck(): Promise<{ status: string }> {
  return request('/health')
}
