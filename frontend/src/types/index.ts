export interface Money {
  amount: number
  currency: string
}

export interface SalaryRange {
  min_amount: Money | null
  max_amount: Money | null
  gross: boolean | null
}

export interface VacancyCreateRequest {
  source_id: string
  external_id: string
  title: string
  url: string
  salary: SalaryRange
  description?: string
  company_id?: string | null
  company_name?: string | null
  location?: string | null
  employment_type?: string | null
  work_mode?: string | null
  published_at?: string | null
  raw_data?: Record<string, unknown> | null
  skill_names?: string[] | null
}

export interface VacancyUpdateRequest {
  title?: string
  description?: string | null
  url?: string
  location?: string | null
  employment_type?: string | null
  work_mode?: string | null
  status?: string | null
  company_id?: string | null
  salary?: SalaryRange | null
  raw_data?: Record<string, unknown> | null
  skill_names?: string[] | null
}

export interface Skill {
  id: string
  name: string
}

export interface Metric {
  salary_min: Money | null
  salary_max: Money | null
  scam_score: number
  apply_score: number
  confidence: number
  details: Record<string, unknown>
  calculated_at: string | null
}

export interface VacancyResponse {
  id: string
  source_id: string
  external_id: string
  title: string
  url: string
  description: string
  company_id: string | null
  company_name: string | null
  location: string | null
  employment_type: string | null
  work_mode: string | null
  published_at: string | null
  status: string
  skills: Skill[]
  metric: Metric | null
  created_at: string
  updated_at: string
}

export type SourceType = 'telegram_channel' | 'career_site' | 'job_board' | 'other'

export type VacancyStatus = 'new' | 'processed' | 'archived'

export interface SourceCreateRequest {
  name: string
  type: SourceType
  url: string
}

export interface SourceUpdateRequest {
  name?: string
  type?: SourceType
  url?: string
  enabled?: boolean
}

export interface SourceResponse {
  id: string
  name: string
  type: SourceType
  url: string
  enabled: boolean
  created_at: string
  updated_at: string
}

export interface CompanyCreateRequest {
  name: string
  website?: string | null
  description?: string | null
}

export interface CompanyResponse {
  id: string
  name: string
  website: string | null
  description: string | null
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export const EMPLOYMENT_TYPES = [
  { value: 'full_time', label: 'Full-time' },
  { value: 'part_time', label: 'Part-time' },
  { value: 'contract', label: 'Contract' },
  { value: 'internship', label: 'Internship' },
  { value: 'freelance', label: 'Freelance' },
] as const

export const WORK_MODES = [
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'office', label: 'Office' },
] as const

export const CURRENCIES = [
  { value: 'RUB', label: '₽ RUB' },
  { value: 'USD', label: '$ USD' },
  { value: 'EUR', label: '€ EUR' },
  { value: 'KZT', label: '₸ KZT' },
  { value: 'BYN', label: 'Br BYN' },
  { value: 'OTHER', label: 'Other' },
] as const

export const VACANCY_STATUSES = [
  { value: 'new', label: 'New', color: '#3b82f6' },
  { value: 'processed', label: 'Processed', color: '#22c55e' },
  { value: 'archived', label: 'Archived', color: '#6b7280' },
] as const

export const SOURCE_TYPES: { value: SourceType; label: string; color: string }[] = [
  { value: 'telegram_channel', label: 'Telegram Channel', color: '#2563eb' },
  { value: 'career_site', label: 'Career Site', color: '#059669' },
  { value: 'job_board', label: 'Job Board', color: '#d97706' },
  { value: 'other', label: 'Other', color: '#6b7280' },
]

export function generateId(): string {
  return crypto.randomUUID()
}
