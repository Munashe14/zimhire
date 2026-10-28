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

type ViewKey = 'dashboard' | 'equipment' | 'clients' | 'bookings' | 'reports' | 'admin'
type FormMode = 'create' | 'edit'

type RoleGateProps = {
  user: User | null
  roles: string[]
  children: React.ReactNode
}

const allowedViewsByRole: Record<string, ViewKey[]> = {
  clerk: ['dashboard', 'equipment', 'clients', 'bookings'],
  supervisor: ['dashboard', 'equipment', 'bookings', 'reports'],
  manager: ['dashboard', 'equipment', 'clients', 'bookings', 'reports', 'admin'],
  client: ['dashboard', 'bookings'],
}

function RoleGate({ user, roles, children }: RoleGateProps) {
  if (!user) {
    return null
  }

  return roles.includes(user.role) ? <>{children}</> : null
}

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
  const [clients, setClients] = useState<Array<{ id: number; full_name: string; phone_number: string; client_type: string }>>([])
  const [activeView, setActiveView] = useState<ViewKey>('dashboard')
  const [equipmentForm, setEquipmentForm] = useState({
    identification_number: '',
    name: '',
    description: '',
    category_id: '1',
    daily_rate: '1500',
    currency: 'USD',
    status: 'available',
  })
  const [clientForm, setClientForm] = useState({
    full_name: '',
    business_name: '',
    phone_number: '+263',
    email: '',
    address: '',
    client_type: 'individual',
  })
  const [formMode, setFormMode] = useState<FormMode>('create')
  const [quickNotice, setQuickNotice] = useState('')

  const hasSession = Boolean(localStorage.getItem('zimhire_access_token'))

  useEffect(() => {
    const storedUser = localStorage.getItem('zimhire_user')
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser) as User
        setUser(parsed)
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

    const loadClients = async () => {
      if (!['clerk', 'manager', 'supervisor'].includes(user.role)) {
        return
      }

      try {
        const response = await api.get<{ items: Array<{ id: number; full_name: string; phone_number: string; client_type: string }> }>('/api/clients', {
          params: { limit: 20 },
        })
        setClients(response.data.items)
      } catch (loadError) {
        console.error(loadError)
      }
    }

    void loadEquipment()
    void loadClients()
  }, [user])

  const summary = useMemo(() => {
    const available = equipment.filter((item) => item.status === 'available').length
    const rented = equipment.filter((item) => item.status === 'rented_out').length
    const maintenance = equipment.filter((item) => item.status === 'under_maintenance').length

    return { available, rented, maintenance }
  }, [equipment])

  const userRole = user?.role ?? 'client'
  const visibleViews = allowedViewsByRole[userRole] ?? ['dashboard']

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

  const handleEquipmentSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    try {
      await api.post('/api/equipment', {
        ...equipmentForm,
        category_id: Number(equipmentForm.category_id),
        daily_rate: Number(equipmentForm.daily_rate),
      })

      setEquipmentForm({
        identification_number: '',
        name: '',
        description: '',
        category_id: '1',
        daily_rate: '1500',
        currency: 'USD',
        status: 'available',
      })
      setFormMode('create')
      const response = await api.get<EquipmentListResponse>('/api/equipment', { params: { limit: 20 } })
      setEquipment(response.data.items)
    } catch (submitError: unknown) {
      console.error(submitError)
    }
  }

  const handleClientSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    try {
      await api.post('/api/clients', {
        ...clientForm,
        client_type: clientForm.client_type,
      })

      setClientForm({
        full_name: '',
        business_name: '',
        phone_number: '+263',
        email: '',
        address: '',
        client_type: 'individual',
      })

      const response = await api.get<{ items: Array<{ id: number; full_name: string; phone_number: string; client_type: string }> }>('/api/clients', {
        params: { limit: 20 },
      })
      setClients(response.data.items)
    } catch (submitError: unknown) {
      console.error(submitError)
    }
  }

  const handleNewForm = () => {
    setFormMode('create')
    setQuickNotice('New record form is ready for entry.')

    if (activeView !== 'equipment' && activeView !== 'clients') {
      setActiveView('equipment')
    }
  }

  const handlePaymentAction = (method: 'ecocash' | 'zipit') => {
    const label = method === 'ecocash' ? 'EcoCash' : 'ZIPIT'
    setQuickNotice(`${label} payment flow opened. Match the record in the reconciliation queue before finishing.`)
    setActiveView('dashboard')
  }

  const handleLogout = () => {
    localStorage.removeItem('zimhire_access_token')
    localStorage.removeItem('zimhire_refresh_token')
    localStorage.removeItem('zimhire_user')
    setUser(null)
    setEquipment([])
    setClients([])
  }

  const renderDashboard = () => (
    <>
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
    </>
  )

  const renderEquipment = () => (
    <div className="panel-grid">
      <section className="table-card form-card">
        <div className="table-header">
          <div>
            <span className="eyebrow">Equipment</span>
            <h3>{formMode === 'create' ? 'Add equipment' : 'Edit equipment'}</h3>
          </div>
        </div>

        <form className="stacked-form" onSubmit={handleEquipmentSubmit}>
          <div className="field-group">
            <label htmlFor="equipmentName">Name</label>
            <input id="equipmentName" value={equipmentForm.name} onChange={(event) => setEquipmentForm({ ...equipmentForm, name: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="assetTag">Asset tag</label>
            <input id="assetTag" value={equipmentForm.identification_number} onChange={(event) => setEquipmentForm({ ...equipmentForm, identification_number: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="equipmentDescription">Description</label>
            <input id="equipmentDescription" value={equipmentForm.description} onChange={(event) => setEquipmentForm({ ...equipmentForm, description: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="categoryId">Category ID</label>
            <input id="categoryId" type="number" value={equipmentForm.category_id} onChange={(event) => setEquipmentForm({ ...equipmentForm, category_id: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="dailyRate">Daily rate</label>
            <input id="dailyRate" type="number" value={equipmentForm.daily_rate} onChange={(event) => setEquipmentForm({ ...equipmentForm, daily_rate: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="equipmentStatus">Status</label>
            <select id="equipmentStatus" value={equipmentForm.status} onChange={(event) => setEquipmentForm({ ...equipmentForm, status: event.target.value })}>
              <option value="available">Available</option>
              <option value="rented_out">Rented</option>
              <option value="under_maintenance">Maintenance</option>
              <option value="returned">Returned</option>
            </select>
          </div>
          <button type="submit" className="primary-button">Save equipment</button>
        </form>
      </section>

      <section className="table-card">
        <div className="table-header">
          <div>
            <span className="eyebrow">Inventory</span>
            <h3>Equipment list</h3>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Asset tag</th>
                <th>Status</th>
                <th>Daily rate</th>
              </tr>
            </thead>
            <tbody>
              {equipment.map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>{item.identification_number}</td>
                  <td>{item.status}</td>
                  <td>{item.daily_rate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )

  const renderClients = () => (
    <div className="panel-grid">
      <section className="table-card form-card">
        <div className="table-header">
          <div>
            <span className="eyebrow">Clients</span>
            <h3>Add client</h3>
          </div>
        </div>

        <form className="stacked-form" onSubmit={handleClientSubmit}>
          <div className="field-group">
            <label htmlFor="fullNameInput">Full name</label>
            <input id="fullNameInput" value={clientForm.full_name} onChange={(event) => setClientForm({ ...clientForm, full_name: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="businessName">Business</label>
            <input id="businessName" value={clientForm.business_name} onChange={(event) => setClientForm({ ...clientForm, business_name: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="phoneNumber">Phone</label>
            <input id="phoneNumber" value={clientForm.phone_number} onChange={(event) => setClientForm({ ...clientForm, phone_number: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="clientEmail">Email</label>
            <input id="clientEmail" type="email" value={clientForm.email} onChange={(event) => setClientForm({ ...clientForm, email: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="clientAddress">Address</label>
            <input id="clientAddress" value={clientForm.address} onChange={(event) => setClientForm({ ...clientForm, address: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor="clientType">Client type</label>
            <select id="clientType" value={clientForm.client_type} onChange={(event) => setClientForm({ ...clientForm, client_type: event.target.value })}>
              <option value="individual">Individual</option>
              <option value="business">Business</option>
            </select>
          </div>
          <button type="submit" className="primary-button">Create client</button>
        </form>
      </section>

      <section className="table-card">
        <div className="table-header">
          <div>
            <span className="eyebrow">Clients</span>
            <h3>Client directory</h3>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Phone</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((client) => (
                <tr key={client.id}>
                  <td>{client.full_name}</td>
                  <td>{client.phone_number}</td>
                  <td>{client.client_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )

  const renderBookings = () => (
    <section className="table-card">
      <div className="table-header">
        <div>
          <span className="eyebrow">Bookings</span>
          <h3>Booking queue</h3>
        </div>
      </div>
      <div className="placeholder-panel">
        <p>Booking create, availability checks, and client-scoped booking requests are available on the backend and can be completed from the role-specific pages once the client portal is connected.</p>
      </div>
    </section>
  )

  const renderReports = () => (
    <section className="table-card">
      <div className="table-header">
        <div>
          <span className="eyebrow">Reports</span>
          <h3>Fleet and revenue reports</h3>
        </div>
      </div>
      <div className="placeholder-panel">
        <p>Report filters are enforced on the server. Use the report endpoints from the API for dashboard, revenue, and utilization queries.</p>
      </div>
    </section>
  )

  const renderAdmin = () => (
    <section className="table-card">
      <div className="table-header">
        <div>
          <span className="eyebrow">Administration</span>
          <h3>User management</h3>
        </div>
      </div>
      <div className="placeholder-panel">
        <p>Manager-only admin views are available through the backend endpoints for users and audit logs.</p>
      </div>
    </section>
  )

  const currentViewRenderer = {
    dashboard: renderDashboard,
    equipment: renderEquipment,
    clients: renderClients,
    bookings: renderBookings,
    reports: renderReports,
    admin: renderAdmin,
  }

  if (!user && !hasSession) {
    return (
      <div className="login-shell">
        <div className="login-card">
          <div className="brand-block">
            <span className="eyebrow">ZimHire</span>
            <h1>Equipment Rental Management</h1>
            <p>Secure fleet coordination, rental operations, and booking oversight in one place.</p>
          </div>

          <form className="login-form" onSubmit={mode === 'signin' ? handleLogIn : handleSignUp}>
            <div className="auth-toggle" role="tablist" aria-label="Authentication mode">
              <button type="button" className={mode === 'signin' ? 'toggle-button active' : 'toggle-button'} onClick={() => setMode('signin')}>
                Sign in
              </button>
              <button type="button" className={mode === 'signup' ? 'toggle-button active' : 'toggle-button'} onClick={() => setMode('signup')}>
                Sign up
              </button>
            </div>

            {mode === 'signup' ? (
              <>
                <div className="field-group">
                  <label htmlFor="fullName">Full name</label>
                  <input id="fullName" type="text" value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Your full name" />
                </div>
                <div className="field-group">
                  <label htmlFor="email">Email</label>
                  <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" />
                </div>
              </>
            ) : null}

            <div className="field-group">
              <label htmlFor="username">Username</label>
              <input id="username" type="text" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Enter username" />
            </div>

            <div className="field-group">
              <label htmlFor="password">Password</label>
              <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter password" />
            </div>

            {mode === 'signup' ? (
              <div className="field-group">
                <label htmlFor="confirmPassword">Confirm password</label>
                <input id="confirmPassword" type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} placeholder="Confirm password" />
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
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand-block small-brand">
          <span className="eyebrow">ZimHire</span>
          <h3>Role portal</h3>
        </div>

        <nav className="menu-list">
          {visibleViews.map((view) => (
            <button
              key={view}
              type="button"
              className={activeView === view ? 'menu-item active' : 'menu-item'}
              onClick={() => setActiveView(view)}
            >
              {view.charAt(0).toUpperCase() + view.slice(1)}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="role-pill">{user?.role ?? 'client'}</span>
          <button type="button" className="secondary-button" onClick={handleLogout}>Log out</button>
        </div>
      </aside>

      <main className="content-panel">
        <header className="topbar">
          <div>
            <span className="eyebrow">Operations Console</span>
            <h2>{user?.full_name ?? 'Portal user'}</h2>
          </div>
        </header>

        <RoleGate user={user} roles={['manager', 'clerk', 'supervisor']}>
          <div className="toolbar-row">
            <button type="button" className="secondary-button" onClick={handleNewForm}>New form</button>
            <button type="button" className="secondary-button" onClick={() => window.location.reload()}>Refresh</button>
          </div>
        </RoleGate>

        <RoleGate user={user} roles={['client']}>
          <div className="toolbar-row">
            <button type="button" className="payment-button ecocash-button" onClick={() => handlePaymentAction('ecocash')}>EcoCash</button>
            <button type="button" className="payment-button zipit-button" onClick={() => handlePaymentAction('zipit')}>ZIPIT</button>
          </div>
        </RoleGate>

        {quickNotice ? <div className="notice-banner">{quickNotice}</div> : null}

        {currentViewRenderer[activeView]()} 
      </main>
    </div>
  )
}

export default App
