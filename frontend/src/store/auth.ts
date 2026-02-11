import { create } from 'zustand'
import { User } from '@/types'

interface AuthStore {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
  setUser: (user: User | null) => void
  setToken: (token: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  logout: () => void
}

const STORAGE_KEY = 'auth_token'

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem(STORAGE_KEY),
  isLoading: false,
  error: null,
  setUser: (user) => set({ user }),
  setToken: (token) => {
    localStorage.setItem(STORAGE_KEY, token)
    set({ token })
  },
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  logout: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({ user: null, token: null, error: null })
  },
}))
