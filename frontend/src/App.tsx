import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import { Header } from '@/components/Header'
import { Sidebar } from '@/components/Sidebar'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import Dashboard from '@/pages/Dashboard'
import Releases from '@/pages/Releases'
import Deployments from '@/pages/Deployments'
import Services from '@/pages/Services'
import Analytics from '@/pages/Analytics'
import AuditLogs from '@/pages/AuditLogs'
import Runbooks from '@/pages/Runbooks'
import Settings from '@/pages/Settings'
import Login from '@/pages/Login'
import * as authApi from '@/api/auth'

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          isSidebarOpen={sidebarOpen}
        />
        <main className="flex-1 overflow-y-auto">
          <div className="p-6 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, token, setUser, isLoading, setLoading, setError } = useAuthStore()
  const [isInitializing, setIsInitializing] = useState(true)

  useEffect(() => {
    const initializeAuth = async () => {
      if (!token) {
        setIsInitializing(false)
        return
      }

      setLoading(true)
      try {
        const currentUser = await authApi.getMe()
        setUser(currentUser)
      } catch (error) {
        setError('Failed to authenticate')
        useAuthStore.getState().logout()
      } finally {
        setLoading(false)
        setIsInitializing(false)
      }
    }

    initializeAuth()
  }, [token])

  if (isInitializing || isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-950">
        <LoadingSpinner text="Loading application..." />
      </div>
    )
  }

  if (!user || !token) {
    return <Navigate to="/login" replace />
  }

  return <ProtectedLayout>{children}</ProtectedLayout>
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/releases"
          element={
            <ProtectedRoute>
              <Releases />
            </ProtectedRoute>
          }
        />
        <Route
          path="/deployments"
          element={
            <ProtectedRoute>
              <Deployments />
            </ProtectedRoute>
          }
        />
        <Route
          path="/services"
          element={
            <ProtectedRoute>
              <Services />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <Analytics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/audit-logs"
          element={
            <ProtectedRoute>
              <AuditLogs />
            </ProtectedRoute>
          }
        />
        <Route
          path="/runbooks"
          element={
            <ProtectedRoute>
              <Runbooks />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  )
}

export default App
