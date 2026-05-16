import { useState } from 'react'

function fmt(min) {
  if (!min) return '--'
  const h = Math.floor(min / 60), m = min % 60
  return `${h}h ${m}m`
}

function formatSeatLabel(status) {
  if (!status) return 'Unknown'
  return String(status).replace(/_/g, ' ')
}

function SeatAvailability({ route, searchDate, isBest, seatFilterReason, seatFilterFallback }) {
  const [open, setOpen] = useState(isBest)
  const checks = route.seat_checks || []
  const allAvailable = route.seat_available ?? checks.every(check => check.available)
  const providerUnavailable = seatFilterReason === 'seat_api_unavailable' || seatFilterFallback
  const trainName = route.legs?.[0]?.train_name || 'Train'

  return (
    <div className="seat-box">
      <button type="button" className="seat-box-toggle" onClick={() => setOpen(v => !v)}>
        <span>Live seat availability</span>
        <span className={`seat-box-chevron${open ? ' open' : ''}`}>⌄</span>
      </button>

      {open && (
        <div className="seat-box-body">
          <div className="seat-summary-row">
            <div>
              <strong>{route.legs?.[0]?.train_no || 'Train'} {route.legs?.[0]?.train_name ? `• ${trainName}` : ''}</strong>
              <span>
                {providerUnavailable
                  ? `Seat API unavailable for ${searchDate || 'this date'}; showing the route and waiting for a live seat response.`
                  : `Live seats confirmed for ${searchDate || route.seat_checks?.[0]?.date || 'this date'}`}
              </span>
            </div>
            <div className={`seat-status-pill ${providerUnavailable ? 'unavailable' : (allAvailable ? 'available' : 'unavailable')}`}>
              {providerUnavailable ? 'Seat API unavailable' : (allAvailable ? 'Seats available' : 'No seats')}
            </div>
          </div>

          {providerUnavailable ? (
            <div className="seat-chip muted">The live seat provider is blocked for this key, so the app is showing the route without seat verification.</div>
          ) : (
            <div className="seat-grid">
              {checks.map((check, index) => (
                <div key={index} className="seat-chip">
                  <strong>{check.from_code} → {check.to_code}</strong>
                  <span>{check.class_code} • {check.date}</span>
                  <span>{formatSeatLabel(check.raw_status || (check.available ? 'AVAILABLE' : 'NOT AVAILABLE'))}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
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

export default function RouteCard({ route, index, searchDate, seatFilterReason, seatFilterFallback }) {
  const isBest = index === 0
  const isDirect = route.num_changes === 0

  return (
    <div className={`route-card${isBest ? ' best' : ''}`}>
      <div className="route-card-topline">
        <div className="route-card-city">
          <span className="route-card-city-code">{route.legs?.[0]?.from_code || route.legs?.[0]?.from || '—'}</span>
          <span className="route-card-city-name">{route.legs?.[0]?.from_name || 'Origin'}</span>
        </div>
        <div className="route-card-divider">to</div>
        <div className="route-card-city route-card-city-right">
          <span className="route-card-city-code">{route.legs?.[route.legs.length - 1]?.to_code || route.legs?.[route.legs.length - 1]?.to || '—'}</span>
          <span className="route-card-city-name">{route.legs?.[route.legs.length - 1]?.to_name || 'Destination'}</span>
        </div>
      </div>

      <div className="route-card-header">
        <div className="route-badges">
          {isBest && <span className="badge badge-best">Recommended</span>}
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

      <SeatAvailability
        route={route}
        searchDate={searchDate}
        isBest={isBest}
        seatFilterReason={seatFilterReason}
        seatFilterFallback={seatFilterFallback}
      />
    </div>
  )
}
