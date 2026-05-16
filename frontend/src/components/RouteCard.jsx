function fmt(min) {
  if (!min) return '--'
  const h = Math.floor(min / 60), m = min % 60
  return `${h}h ${m}m`
}

function LegBar({ leg }) {
  return (
    <div className="leg-row">
      <div className="leg-time">
        {leg.departure}
        <small>{leg.from_name || leg.train_no}</small>
      </div>
      <div className="leg-bar">
        <span className="leg-train-name">{leg.train_name} ({leg.train_no})</span>
        <div className="leg-line" />
        <span className="leg-duration">{fmt(leg.duration_min)}</span>
      </div>
      <div className="leg-time" style={{ textAlign: 'right' }}>
        {leg.arrival}
        <small>{leg.to_name}</small>
      </div>
    </div>
  )
}

export default function RouteCard({ route, index }) {
  const isBest = index === 0
  const isDirect = route.num_changes === 0

  return (
    <div className={`route-card${isBest ? ' best' : ''}`}>
      <div className="route-card-header">
        <div className="route-badges">
          {isBest && <span className="badge badge-best">⭐ Best Match</span>}
          {isDirect
            ? <span className="badge badge-direct">✓ Direct</span>
            : <span className="badge badge-connect">{route.num_changes} Change{route.num_changes > 1 ? 's' : ''}</span>
          }
        </div>
        <span className="route-duration">{route.total_duration_human}</span>
      </div>

      <div className="route-legs">
        {route.legs.map((leg, i) => (
          <div key={i}>
            {i > 0 && (
              <div className="connection-gap">
                <div className="connection-gap-line" />
                <span>🔄 Change at {route.legs[i - 1].to_name} — {route.total_wait_min} min wait</span>
                <div className="connection-gap-line" />
              </div>
            )}
            <LegBar leg={leg} />
          </div>
        ))}
      </div>

      <div className="stats-bar">
        <div className="stat-item">🕐 <strong>{fmt(route.total_duration_min)}</strong> total</div>
        {route.total_wait_min > 0 && (
          <div className="stat-item">⏳ <strong>{fmt(route.total_wait_min)}</strong> wait</div>
        )}
        <div className="stat-item">🚂 <strong>{route.trains.join(', ')}</strong></div>
      </div>
    </div>
  )
}
