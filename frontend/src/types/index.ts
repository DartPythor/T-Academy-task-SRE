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

export function generateId(): string {
  return crypto.randomUUID()
}
