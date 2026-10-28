export type UserRole =
  | 'clerk'
  | 'supervisor'
  | 'manager'
  | 'client'
  | 'admin'
  | 'booking_clerk'
  | 'depot_supervisor'
  | 'operations_manager'

export type User = {
  id: number
  username: string
  email?: string | null
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  last_login?: string | null
}

export type TokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export type Equipment = {
  id: number
  identification_number: string
  name: string
  category_id: number
  description?: string | null
  specifications?: string | null
  daily_rate: string
  currency: string
  status: string
  maintenance_notes?: string | null
  created_at: string
  updated_at?: string | null
  category?: {
    id: number
    name: string
    description?: string | null
    created_at: string
    updated_at?: string | null
  } | null
}

export type EquipmentListResponse = {
  items: Equipment[]
  total: number
  skip: number
  limit: number
}
