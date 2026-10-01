interface MetricCardProps {
  title: string
  value: number
  max: number
  color: 'red' | 'amber' | 'emerald'
  subtitle: string
  isLoading: boolean
}

function CardIcon({ color }: { color: string }) {
  // Scam Alert icon for red, Thumbs Up for emerald, Warning for amber
  const icon = color === 'red'
    ? 'M12 7v10l5 5-10m-5-5v-10M17 15a3 3 0 01-3 1 3 1 3-3 0 3-1-3-1-3 3'
    : color === 'emerald'
    ? 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
    : 'M12 3v3M17 7v4M20 10l-8-8M7 15v-2M10 17v5'

  return (
    <svg width={16} height={16} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" d={icon} />
    </svg>
  )
}

export function MetricCard({ title, value, max, color, subtitle, isLoading }: MetricCardProps) {
  const pct = Math.min((value / max) * 100, 100)

  return (
    <div className={`metric-card card-${color} ${isLoading ? 'loading' : ''}`}>
      <div className="metric-card-header">
        <span>{title}</span>
        <div className="metric-icon">
          <CardIcon color={color} />
        </div>
      </div>

      <div className="metric-value">
        {isLoading ? (
          <span className="skeleton" />
        ) : (
          <span>{value}</span>
        )}
        <span className="metric-max">/ {max}</span>
      </div>

      <div className="metric-bar">
        <div className="metric-bar-fill" style={{ width: isLoading ? '0%' : `${pct}%` }} />
      </div>

      <p className="metric-subtitle">
        {isLoading ? <span className="skeleton" /> : subtitle}
      </p>
    </div>
  )
}