import { useState, useEffect, useRef } from 'react'
import { stationSearch } from '../services/api'

export default function StationInput({ label, value, onChange, placeholder, id }) {
  const [query, setQuery] = useState(value || '')
  const [suggestions, setSuggestions] = useState([])
  const [open, setOpen] = useState(false)
  const timer = useRef(null)
  const wrapRef = useRef(null)

  useEffect(() => {
    const handleClick = (e) => { if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const handleChange = (e) => {
    const val = e.target.value
    setQuery(val)
    onChange({ code: '', name: val })
    clearTimeout(timer.current)
    if (val.length >= 2) {
      timer.current = setTimeout(async () => {
        try {
          const res = await stationSearch(val)
          setSuggestions(res.data.stations || [])
          setOpen(true)
        } catch { setSuggestions([]) }
      }, 300)
    } else {
      setSuggestions([])
      setOpen(false)
    }
  }

  const select = (s) => {
    setQuery(`${s.name} (${s.code})`)
    onChange({ code: s.code, name: s.name })
    setOpen(false)
    setSuggestions([])
  }

  return (
    <div className="search-field autocomplete-wrap" ref={wrapRef}>
      <label className="search-label" htmlFor={id}>{label}</label>
      <input
        id={id}
        className="search-input"
        value={query}
        onChange={handleChange}
        placeholder={placeholder}
        autoComplete="off"
        onFocus={() => suggestions.length > 0 && setOpen(true)}
      />
      {open && suggestions.length > 0 && (
        <div className="autocomplete-list">
          {suggestions.map((s) => (
            <div key={s.code} className="autocomplete-item" onMouseDown={() => select(s)}>
              <span className="autocomplete-code">{s.code}</span>
              <span className="autocomplete-name">{s.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
