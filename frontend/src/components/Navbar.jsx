import { Link, useLocation } from 'react-router-dom'
import { Train } from 'lucide-react'

export default function Navbar() {
  const { pathname } = useLocation()
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo">
        <Train size={22} />
        Pridicto
      </Link>
      <div className="navbar-links">
        <Link to="/" className={`navbar-link${pathname === '/' ? ' active' : ''}`}>Home</Link>
        <Link to="/search" className={`navbar-link${pathname === '/search' ? ' active' : ''}`}>Search</Link>
        <Link to="/about" className={`navbar-link${pathname === '/about' ? ' active' : ''}`}>About</Link>
        <Link to="/search" className="navbar-cta">Plan a Trip →</Link>
      </div>
    </nav>
  )
}
