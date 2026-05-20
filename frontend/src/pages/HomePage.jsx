import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Zap, GitBranch, Clock } from 'lucide-react'
import { getPopularRoutes } from '../services/api'

const FEATURES = [
  { icon: '->', title: 'Plain-language search', desc: 'Write the trip like you’d ask a clerk at the station counter.' },
  { icon: '->', title: 'Practical route plan', desc: 'Shows routes that make sense for real travel, not just algorithm demos.' },
  { icon: '->', title: 'Fast lookups', desc: 'Repeat searches stay quick with caching and simple data loading.' },
  { icon: '->', title: 'Live status', desc: 'Check running trains and seat info without leaving the page.' },
  { icon: '->', title: 'Change protection', desc: 'Stops unrealistic transfer plans that are too tight to catch.' },
  { icon: '₹0', title: 'Local first', desc: 'Runs locally with free tiers and works even when API keys are missing.' },
]

export default function HomePage() {
  const navigate = useNavigate()
  const [popular, setPopular] = useState([])

  useEffect(() => {
    getPopularRoutes().then(r => setPopular(r.data.popular_routes || [])).catch(() => {})
  }, [])
     
  const go = (from, to) => navigate(`/search?from=${from}&to=${to}`)

  return (
    <div className="page-wrapper">
      {/* Hero */}
      <section className="hero">
        <div className="hero-bg-orb orb1" />
        <div className="hero-bg-orb orb2" />

        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <div className="hero-badge">
            <span className="badge-dot" />
            Find Best Trains
          </div>
          <h1 className="hero-title">
            Plan your next <span className="gradient-text">train trip</span><br />
            with clarity
          </h1>
          <p className="hero-subtitle">
            A calmer, station-style planner for finding routes, checking trains, and seeing seat info in one place.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="search-btn" style={{ fontSize: '1rem', padding: '0.8rem 2rem' }} onClick={() => navigate('/search')}>
              Search Trains <ArrowRight size={18} />
            </button>
            <button
              onClick={() => navigate('/about')}
              style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '10px', padding: '0.8rem 1.5rem', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1rem', fontFamily: 'var(--font)', transition: 'border-color 0.2s' }}
              onMouseOver={e => e.target.style.borderColor = 'var(--accent)'}
              onMouseOut={e => e.target.style.borderColor = 'var(--border)'}
            >
              How it works
            </button>
          </div>
        </motion.div>

        <div className="hero-rail-scene" aria-hidden="true">
          <div className="hero-train">
            <div className="train-engine">
              <div className="train-window-row" />
            </div>
            <div className="train-cab" />
            <div className="train-cab" style={{ opacity: 0.92, transform: 'scaleX(0.95)' }} />
            <div className="train-smoke">
              <span />
              <span />
              <span />
            </div>
          </div>
          <div className="hero-rail-track" />
          <div className="hero-rail-ties" />
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <p className="section-label">Why Pridicto</p>
          <h2 className="section-title">Built like a station board</h2>
          <p className="section-sub">Clear, readable, and focused on the details people actually look for before boarding.</p>
        </motion.div>
        <div className="features-grid">
          {FEATURES.map((f, i) => (
            <motion.div key={i} className="feature-card" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}>
              <span className="feature-icon">{f.icon}</span>
              <div className="feature-title">{f.title}</div>
              <div className="feature-desc">{f.desc}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Popular Routes */}
      {popular.length > 0 && (
        <section className="popular-section">
          <p className="section-label">Quick Search</p>
          <h2 className="section-title" style={{ marginBottom: '1.5rem' }}>Popular Routes</h2>
          <div className="popular-grid">
            {popular.map((r, i) => (
              <motion.div key={i} className="popular-card" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.05 }} onClick={() => go(r.from, r.to)}>
                <span style={{ fontSize: '1.1rem' }}>🚂</span>
                <span className="popular-card-label">{r.label}</span>
              </motion.div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
