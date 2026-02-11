import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import {
  LayoutDashboard,
  Package,
  Rocket,
  FileText,
  BarChart3,
  BookOpen,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react'
import clsx from 'clsx'

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const isActive = (path: string) => location.pathname === path

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: Package, label: 'Releases', path: '/releases' },
    { icon: Rocket, label: 'Deployments', path: '/deployments' },
    { icon: FileText, label: 'Services', path: '/services' },
    { icon: BarChart3, label: 'Analytics', path: '/analytics' },
    { icon: FileText, label: 'Audit Logs', path: '/audit-logs' },
    { icon: BookOpen, label: 'Runbooks', path: '/runbooks' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ]

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed left-0 top-0 h-full w-64 bg-gray-900 border-r border-gray-800 z-40 transition-transform md:relative md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold text-gray-100">Release Mgr</h1>
              <button
                onClick={onClose}
                className="md:hidden text-gray-400 hover:text-gray-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={onClose}
                  className={clsx(
                    'flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-smooth',
                    isActive(item.path)
                      ? 'bg-indigo-600 text-white'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                  )}
                >
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </Link>
              ))}
            </div>
          </nav>

          {/* User section */}
          <div className="border-t border-gray-800 p-4">
            {user && (
              <div className="space-y-4">
                <div className="px-4 py-3 rounded-lg bg-gray-800/50">
                  <p className="text-xs text-gray-400">Logged in as</p>
                  <p className="text-sm font-medium text-gray-100 truncate">
                    {user.name}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {user.email}
                  </p>
                </div>
                <button
                  onClick={() => {
                    logout()
                    window.location.href = '/login'
                  }}
                  className="w-full flex items-center gap-3 px-4 py-2 text-gray-400 hover:text-gray-200 hover:bg-gray-800 rounded-lg transition-smooth text-sm font-medium"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
