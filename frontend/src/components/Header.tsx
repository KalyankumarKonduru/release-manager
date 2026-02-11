import React, { useState } from 'react'
import { Search, Bell, Menu, X, User } from 'lucide-react'
import { useAuthStore } from '@/store/auth'

interface HeaderProps {
  onMenuClick?: () => void
  isSidebarOpen?: boolean
}

export function Header({ onMenuClick, isSidebarOpen = true }: HeaderProps) {
  const { user } = useAuthStore()
  const [showNotifications, setShowNotifications] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <header className="sticky top-0 z-20 bg-gray-900/95 backdrop-blur border-b border-gray-800">
      <div className="px-6 py-4 flex items-center justify-between gap-4">
        {/* Menu button for mobile */}
        <button
          onClick={onMenuClick}
          className="md:hidden text-gray-400 hover:text-gray-200"
        >
          {isSidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>

        {/* Search bar */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search deployments, releases..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-10 py-2 text-sm"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-gray-400 hover:text-gray-200 hover:bg-gray-800 rounded-lg transition-smooth"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-xl">
                <div className="p-4 border-b border-gray-700">
                  <h3 className="font-semibold text-gray-100">Notifications</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  <div className="p-4">
                    <p className="text-sm text-gray-400 text-center">
                      No new notifications
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* User avatar */}
          {user && (
            <div className="flex items-center gap-3 pl-4 border-l border-gray-700">
              <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-gray-100">{user.name}</p>
                <p className="text-xs text-gray-500">{user.role}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
