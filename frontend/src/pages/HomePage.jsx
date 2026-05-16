import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Zap, GitBranch, Clock } from 'lucide-react'
import { getPopularRoutes } from '../services/api'

const FEATURES = [
  { icon: '🧠', title: 'AI-Powered Search', desc: 'Type naturally — "trains from Kota to Patna avoiding long waits" — Claude understands you.' },
  { icon: '🗺️', title: 'Smart Route Graph', desc: 'BFS graph engine finds optimal multi-hop connections other apps miss entirely.' },
  { icon: '⚡', title: 'Redis-Cached Speed', desc: 'Schedules cached 6 hours. Zero wait on repeat searches. Blazing fast always.' },
  { icon: '🔴', title: 'Live Train Status', desc: 'Real-time running status for any train in India, right inside the app.' },
  { icon: '🔗', title: 'Connection Validation', desc: 'Minimum 30-min buffer enforced. No impossible connections ever suggested.' },
  { icon: '₹0', title: 'Completely Free', desc: 'Built on Vercel, Railway.app, Supabase and Upstash — zero monthly cost.' },
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
            Powered by Claude AI + BFS Graph Engine
          </div>
          <h1 className="hero-title">
            Find the <span className="gradient-text">Smartest</span><br />
            Train Route in India
          </h1>
          <p className="hero-subtitle">
            Pridicto uses a graph algorithm + AI to discover optimal multi-hop train journeys.
            Search naturally, get ranked results instantly.
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
      </section>

      {/* Features */}
      <section className="features-section">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <p className="section-label">Why Pridicto</p>
          <h2 className="section-title">Built different, by design</h2>
          <p className="section-sub">Not just a schedule lookup — a route intelligence engine that thinks in graphs and speaks human.</p>
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
