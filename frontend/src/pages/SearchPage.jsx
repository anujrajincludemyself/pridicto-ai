import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Sparkles, ArrowLeftRight } from 'lucide-react'
import StationInput from '../components/StationInput'
import RouteCard from '../components/RouteCard'
import { searchRoutes, aiSearch } from '../services/api'

const today = () => new Date().toISOString().split('T')[0]

export default function SearchPage() {
  const [params] = useSearchParams()
  const [tab, setTab] = useState('standard') // 'standard' | 'ai'
  const [from, setFrom] = useState({ code: params.get('from') || '', name: '' })
  const [to, setTo] = useState({ code: params.get('to') || '', name: '' })
  const [date, setDate] = useState(today())
  const [aiQuery, setAiQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [aiSummary, setAiSummary] = useState('')
  const [error, setError] = useState('')

  // Auto-search if URL params set
  useEffect(() => {
    if (params.get('from') && params.get('to')) {
      handleStandardSearch(params.get('from'), params.get('to'))
    }
  }, [])

  const handleStandardSearch = async (fromCode, toCode) => {
    const f = fromCode || from.code
    const t = toCode || to.code
    if (!f || !t) { setError('Please select both origin and destination stations.'); return }
    setError(''); setLoading(true); setResults(null); setAiSummary('')
    try {
      const dateFormatted = date.replace(/-/g, '')
      const res = await searchRoutes(f, t, dateFormatted)
      setResults(res.data.routes || [])
    } catch (e) {
      setError(e.response?.data?.error || 'Search failed. Is the backend running?')
    } finally { setLoading(false) }
  }

  const handleAiSearch = async () => {
    if (!aiQuery.trim()) { setError('Please enter a search query.'); return }
    setError(''); setLoading(true); setResults(null); setAiSummary('')
    try {
      const res = await aiSearch(aiQuery)
      setResults(res.data.routes || [])
      setAiSummary(res.data.ai_summary || '')
    } catch (e) {
      setError(e.response?.data?.error || 'AI search failed.')
    } finally { setLoading(false) }
  }

  const swap = () => {
    setFrom(to)
    setTo(from)
  }

  return (
    <div className="page-wrapper">
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '3rem 1.5rem' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700, marginBottom: '0.4rem' }}>
            Search Trains
          </h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', fontSize: '0.95rem' }}>
            Find optimal routes across India — direct or with connections
          </p>

          <div className="search-card">
            <div className="search-tabs">
              <button id="tab-standard" className={`search-tab${tab === 'standard' ? ' active' : ''}`} onClick={() => setTab('standard')}>
                🔍 Standard Search
              </button>
              <button id="tab-ai" className={`search-tab${tab === 'ai' ? ' active' : ''}`} onClick={() => setTab('ai')}>
                ✨ AI Search
              </button>
            </div>

            {tab === 'standard' ? (
              <>
                <div className="search-row">
                  <StationInput id="station-from" label="From" value={from.code} onChange={setFrom} placeholder="e.g. New Delhi, NDLS" />
                  <div style={{ alignSelf: 'flex-end' }}>
                    <button id="btn-swap" className="swap-btn" onClick={swap} title="Swap stations">⇄</button>
                  </div>
                  <StationInput id="station-to" label="To" value={to.code} onChange={setTo} placeholder="e.g. Mumbai, BCT" />
                </div>
                <div className="search-bottom">
                  <div className="search-field">
                    <label className="search-label" htmlFor="travel-date">Date</label>
                    <input id="travel-date" type="date" className="search-input" value={date} min={today()} onChange={e => setDate(e.target.value)} />
                  </div>
                  <div />
                  <button id="btn-search" className="search-btn" onClick={() => handleStandardSearch()} disabled={loading}>
                    {loading ? <><span className="spinner" /> Searching…</> : <><Search size={16} /> Find Routes</>}
                  </button>
                </div>
              </>
            ) : (
              <>
                <div style={{ marginBottom: '1rem' }}>
                  <label className="search-label" style={{ display: 'block', marginBottom: '0.4rem' }}>Describe your journey</label>
                  <div className="ai-input-wrap">
                    <span className="ai-icon">✨</span>
                    <input
                      id="ai-query-input"
                      className="ai-input"
                      value={aiQuery}
                      onChange={e => setAiQuery(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && handleAiSearch()}
                      placeholder="e.g. trains from Kota to Patna for Chhath Puja with AC coaches"
                    />
                  </div>
                </div>
                <button id="btn-ai-search" className="search-btn" onClick={handleAiSearch} disabled={loading}>
                  {loading ? <><span className="spinner" /> Thinking…</> : <><Sparkles size={16} /> Search with AI</>}
                </button>
              </>
            )}
          </div>
        </motion.div>

        {/* Error */}
        {error && <div className="error-msg">⚠️ {error}</div>}

        {/* Loading skeletons */}
        {loading && (
          <div style={{ marginTop: '2rem' }}>
            {[1, 2, 3].map(i => (
              <div key={i} className="skeleton" style={{ height: 180, marginBottom: '1rem' }} />
            ))}
          </div>
        )}

        {/* Results */}
        <AnimatePresence>
          {results !== null && !loading && (
            <motion.div className="results-section" style={{ padding: '2rem 0' }} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className="results-header">
                <div className="results-count">
                  Found <span>{results.length}</span> route{results.length !== 1 ? 's' : ''}
                </div>
              </div>

              {aiSummary && (
                <div className="ai-summary-box">
                  <strong>✨ AI Summary: </strong>{aiSummary}
                </div>
              )}

              {results.length === 0 ? (
                <div className="empty-state">
                  <span className="empty-state-icon">🚂</span>
                  <h3>No routes found</h3>
                  <p>Try different stations or check if the API key is configured in the backend .env file.</p>
                </div>
              ) : (
                results.map((route, i) => (
                  <motion.div key={i} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                    <RouteCard route={route} index={i} />
                  </motion.div>
                ))
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
