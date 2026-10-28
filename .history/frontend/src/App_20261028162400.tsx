import { useEffect, useMemo, useState } from 'react'
import './App.css'
import { api } from './api'
import type { Equipment, EquipmentListResponse, TokenResponse, User } from './types'

const demoCredentials = [
  { label: 'Manager', username: 'ops_manager', password: 'Manager123!' },
  { label: 'Clerk', username: 'booking_clerk', password: 'Clerk123!' },
  { label: 'Supervisor', username: 'depot_supervisor', password: 'Supervisor123!' },
  { label: 'Client', username: 'client_user', password: 'Client123!' },
]

function App() {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('Admin123!')
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [user, setUser] = useState<User | null>(null)
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [equipmentMeta, setEquipmentMeta] = useState({ total: 0, skip: 0, limit: 10 })

  const hasSession = Boolean(localStorage.getItem('zimhire_access_token'))

  useEffect(() => {
    const storedUser = localStorage.getItem('zimhire_user')
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser) as User)
      } catch {
        localStorage.removeItem('zimhire_user')
      }
    }
  }, [])

  useEffect(() => {
    if (!user) {
      return
    }

    const loadEquipment = async () => {
      try {
        const response = await api.get<EquipmentListResponse>('/api/equipment', {
          params: { limit: 20 },
        })

        setEquipment(response.data.items)
        setEquipmentMeta({
          total: response.data.total,
          skip: response.data.skip,
          limit: response.data.limit,
        })
      } catch (loadError) {
        console.error(loadError)
      }
    }

    void loadEquipment()
  }, [user])

  const summary = useMemo(() => {
    const available = equipment.filter((item) => item.status === 'available').length
    const rented = equipment.filter((item) => item.status === 'rented_out').length
    const maintenance = equipment.filter((item) => item.status === 'under_maintenance').length

    return { available, rented, maintenance }
  }, [equipment])

  const storeAuthSession = (response: TokenResponse) => {
    localStorage.setItem('zimhire_access_token', response.access_token)
    localStorage.setItem('zimhire_refresh_token', response.refresh_token)
    localStorage.setItem('zimhire_user', JSON.stringify(response.user))
    setUser(response.user)
  }

  const handleLogIn = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await api.post<TokenResponse>('/api/auth/login', {
        username,
        password,
      })

      storeAuthSession(response.data)
    } catch (loginError: unknown) {
      if (typeof loginError === 'object' && loginError !== null && 'response' in loginError) {
        const err = loginError as { response?: { data?: { detail?: string } } }
        setError(err.response?.data?.detail ?? 'Unable to sign in. Please check your credentials.')
      } else {
        setError('Unable to sign in right now. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignUp = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      setIsLoading(false)
      return
    }

    try {
      const response = await api.post<TokenResponse>('/api/auth/signup', {
        username,
        full_name: fullName,
        email: email.trim() || undefined,
        password,
        role: 'client',
      })

      storeAuthSession(response.data)
    } catch (signupError: unknown) {
      if (typeof signupError === 'object' && signupError !== null && 'response' in signupError) {
        const err = signupError as { response?: { data?: { detail?: string } } }
        setError(err.response?.data?.detail ?? 'Unable to create your account right now.')
      } else {
        setError('Unable to create your account right now. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('zimhire_access_token')
    localStorage.removeItem('zimhire_refresh_token')
    localStorage.removeItem('zimhire_user')
    setUser(null)
    setEquipment([])
  }

  if (!user && !hasSession) {
    return (
      <div className="login-shell">
        <div className="login-card">
          <div className="brand-block">
            <span className="eyebrow">ZimHire</span>
            <h1>Equipment Rental Management</h1>
            <p>Local SQLite setup for secure fleet and booking operations.</p>
          </div>

          <form className="login-form" onSubmit={mode === 'signin' ? handleLogIn : handleSignUp}>
            <div className="auth-toggle" role="tablist" aria-label="Authentication mode">
              <button
                type="button"
                className={mode === 'signin' ? 'toggle-button active' : 'toggle-button'}
                onClick={() => setMode('signin')}
              >
                Sign in
              </button>
              <button
                type="button"
                className={mode === 'signup' ? 'toggle-button active' : 'toggle-button'}
                onClick={() => setMode('signup')}
              >
                Sign up
              </button>
            </div>

            {mode === 'signup' ? (
              <>
                <div className="field-group">
                  <label htmlFor="fullName">Full name</label>
                  <input
                    id="fullName"
                    type="text"
                    value={fullName}
                    onChange={(event) => setFullName(event.target.value)}
                    placeholder="Your full name"
                  />
                </div>

                <div className="field-group">
                  <label htmlFor="email">Email</label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="you@example.com"
                  />
                </div>
              </>
            ) : null}

            <div className="field-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Enter username"
              />
            </div>

            <div className="field-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter password"
              />
            </div>

            {mode === 'signup' ? (
              <div className="field-group">
                <label htmlFor="confirmPassword">Confirm password</label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="Confirm password"
                />
              </div>
            ) : null}

            {error ? <div className="error-box">{error}</div> : null}

            <button type="submit" className="primary-button" disabled={isLoading}>
              {isLoading ? (mode === 'signin' ? 'Signing in...' : 'Creating account...') : mode === 'signin' ? 'Sign in' : 'Create account'}
            </button>

            {mode === 'signin' ? (
              <div className="demo-row">
                {demoCredentials.map((item) => (
                  <button
                    key={item.username}
                    type="button"
                    className="demo-button"
                    onClick={() => {
                      setUsername(item.username)
                      setPassword(item.password)
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            ) : null}
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">Operations Console</span>
          <h2>Welcome back, {user?.full_name ?? 'Manager'}</h2>
        </div>

        <div className="topbar-actions">
          <span className="role-pill">{user?.role.replace('_', ' ')}</span>
          <button type="button" className="secondary-button" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Available</span>
          <strong>{summary.available}</strong>
        </div>
        <div className="stat-card">
          <span>Rented out</span>
          <strong>{summary.rented}</strong>
        </div>
        <div className="stat-card">
          <span>Maintenance</span>
          <strong>{summary.maintenance}</strong>
        </div>
        <div className="stat-card">
          <span>Total units</span>
          <strong>{equipmentMeta.total}</strong>
        </div>
      </section>

      <section className="table-card">
        <div className="table-header">
          <div>
            <span className="eyebrow">Inventory</span>
            <h3>Equipment overview</h3>
          </div>
          <button type="button" className="secondary-button" onClick={() => window.location.reload()}>
            Refresh
          </button>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Asset</th>
                <th>ID</th>
                <th>Category</th>
                <th>Rate</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {equipment.map((item) => (
                <tr key={item.id}>
                  <td>
                    <div className="asset-cell">
                      <strong>{item.name}</strong>
                      <small>{item.description ?? 'No description'}</small>
                    </div>
                  </td>
                  <td>{item.identification_number}</td>
                  <td>{item.category?.name ?? 'Unassigned'}</td>
                  <td>
                    {item.daily_rate} {item.currency}
                  </td>
                  <td>
                    <span className={`status-badge status-${item.status}`}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default App
