import { useEffect, useState } from 'react'
import { getSeatAvailability } from '../services/api'

function fmt(min) {
  if (!min) return '--'
  const h = Math.floor(min / 60), m = min % 60
  return `${h}h ${m}m`
}

function formatSeatLabel(status) {
  if (!status) return 'Unknown'
  return String(status).replace(/_/g, ' ')
}

function SeatAvailability({ route, searchDate, isBest }) {
  const firstLeg = route.legs?.[0]
  const lastLeg = route.legs?.[route.legs.length - 1]
  const trainNo = firstLeg?.train_no
  const fromCodeValue = firstLeg?.from_code || firstLeg?.from || ''
  const toCodeValue = lastLeg?.to_code || lastLeg?.to || ''
  const classCode = route.legs?.[0]?.classes?.[0] || 'SL'

  const [open, setOpen] = useState(isBest)
  const [loading, setLoading] = useState(false)
  const [availability, setAvailability] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!open || !trainNo || !searchDate || availability) return

    let cancelled = false

    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const response = await getSeatAvailability(
          trainNo,
          fromCodeValue,
          toCodeValue,
          searchDate,
          'GN',
          classCode
        )
        if (!cancelled) {
          setAvailability(response.data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.response?.data?.error || 'Seat availability not available right now.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [availability, classCode, fromCodeValue, open, route.legs, searchDate, toCodeValue, trainNo])

  if (!trainNo) return null

  return (
    <div className="seat-box">
      <button type="button" className="seat-box-toggle" onClick={() => setOpen(v => !v)}>
        <span>Live seat availability</span>
        <span className={`seat-box-chevron${open ? ' open' : ''}`}>⌄</span>
      </button>

      {open && (
        <div className="seat-box-body">
          {loading && <div className="seat-loading">Checking seats for {classCode}...</div>}

          {!loading && error && <div className="seat-error">{error}</div>}

          {!loading && availability && !error && (
            <>
              <div className="seat-summary-row">
                <div>
                  <strong>{trainNo}</strong>
                  <span>{route.legs?.[0]?.train_name || 'Train'} • {classCode} • GN</span>
                </div>
                <div className={`seat-status-pill ${availability.available ? 'available' : 'unavailable'}`}>
                  {availability.available ? 'Live seats found' : 'No live seats'}
                </div>
              </div>

              <div className="seat-grid">
                {(availability.seats || []).slice(0, 3).map((seat, index) => (
                  <div key={index} className="seat-chip">
                    <strong>{formatSeatLabel(seat.status)}</strong>
                    <span>{seat.date || searchDate}</span>
                    <span>{seat.class_code || classCode} • {seat.quota || 'GN'}</span>
                    {seat.available_seats ? <span>{seat.available_seats}</span> : null}
                  </div>
                ))}
                {(!availability.seats || availability.seats.length === 0) && (
                  <div className="seat-chip muted">No structured seat rows returned by the provider.</div>
                )}
              </div>
            </>
          )}

          {!loading && !availability && !error && (
            <div className="seat-helper">
              Tap to check live seats for this train on {searchDate || 'your selected date'}.
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

export default function RouteCard({ route, index, searchDate }) {
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

      <SeatAvailability route={route} searchDate={searchDate} isBest={isBest} />
    </div>
  )
}
