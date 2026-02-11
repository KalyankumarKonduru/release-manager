import React, { useState } from 'react'
import { useAuthStore } from '@/store/auth'
import { User, Lock, Bell, Shield, Users } from 'lucide-react'

export default function Settings() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
  })
  const [passwordData, setPasswordData] = useState({
    current: '',
    new: '',
    confirm: '',
  })

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'password', label: 'Password', icon: Lock },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'team', label: 'Team', icon: Users },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Settings</h1>
        <p className="text-gray-400 mt-1">
          Manage your account and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card overflow-hidden">
            <div className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-smooth ${
                      activeTab === tab.id
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-100 mb-6">
                Profile Settings
              </h2>

              <form className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Role
                  </label>
                  <input
                    type="text"
                    value={user?.role || ''}
                    disabled
                    className="input-field w-full opacity-50 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Team
                  </label>
                  <input
                    type="text"
                    value={user?.team_id || ''}
                    disabled
                    className="input-field w-full opacity-50 cursor-not-allowed"
                  />
                </div>

                <div className="flex gap-3 pt-4 border-t border-gray-700">
                  <button type="submit" className="btn-primary">
                    Save Changes
                  </button>
                  <button type="button" className="btn-secondary">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Password Tab */}
          {activeTab === 'password' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-100 mb-6">
                Change Password
              </h2>

              <form className="space-y-6 max-w-md">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Current Password
                  </label>
                  <input
                    type="password"
                    value={passwordData.current}
                    onChange={(e) =>
                      setPasswordData({
                        ...passwordData,
                        current: e.target.value,
                      })
                    }
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    New Password
                  </label>
                  <input
                    type="password"
                    value={passwordData.new}
                    onChange={(e) =>
                      setPasswordData({
                        ...passwordData,
                        new: e.target.value,
                      })
                    }
                    className="input-field w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={passwordData.confirm}
                    onChange={(e) =>
                      setPasswordData({
                        ...passwordData,
                        confirm: e.target.value,
                      })
                    }
                    className="input-field w-full"
                  />
                </div>

                <div className="flex gap-3 pt-4 border-t border-gray-700">
                  <button type="submit" className="btn-primary">
                    Update Password
                  </button>
                  <button type="button" className="btn-secondary">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-100 mb-6">
                Notification Preferences
              </h2>

              <div className="space-y-4">
                {[
                  {
                    label: 'Deployment Started',
                    description: 'Notify when a deployment begins',
                  },
                  {
                    label: 'Deployment Completed',
                    description: 'Notify when a deployment finishes',
                  },
                  {
                    label: 'Approval Required',
                    description: 'Notify when deployment approval is needed',
                  },
                  {
                    label: 'Deployment Failed',
                    description: 'Notify when a deployment fails',
                  },
                  {
                    label: 'Daily Summary',
                    description: 'Receive a daily summary of deployments',
                  },
                ].map((notif, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 border border-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-100">{notif.label}</p>
                      <p className="text-sm text-gray-400">{notif.description}</p>
                    </div>
                    <input
                      type="checkbox"
                      defaultChecked
                      className="w-5 h-5 rounded"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-100 mb-6">
                Security Settings
              </h2>

              <div className="space-y-6">
                <div className="border-l-4 border-yellow-600 bg-yellow-900/20 p-4 rounded">
                  <p className="text-sm text-yellow-200">
                    Two-factor authentication is not enabled. Enable it to add an extra layer of security to your account.
                  </p>
                  <button className="mt-3 text-sm text-yellow-400 hover:text-yellow-300 font-medium">
                    Enable 2FA
                  </button>
                </div>

                <div className="pt-6 border-t border-gray-700">
                  <h3 className="font-medium text-gray-100 mb-4">
                    Active Sessions
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-start justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-100">
                          Current Session
                        </p>
                        <p className="text-sm text-gray-400">
                          Chrome on macOS • Last active just now
                        </p>
                      </div>
                      <span className="text-xs px-2 py-1 bg-green-900/30 text-green-300 rounded">
                        Active
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Team Tab */}
          {activeTab === 'team' && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-100 mb-6">
                Team Members
              </h2>

              <div className="space-y-4">
                {[
                  {
                    name: 'You',
                    email: user?.email,
                    role: user?.role,
                  },
                  {
                    name: 'John Developer',
                    email: 'john@example.com',
                    role: 'developer',
                  },
                  {
                    name: 'Jane Manager',
                    email: 'jane@example.com',
                    role: 'release-manager',
                  },
                ].map((member, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 border border-gray-700 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-sm font-medium text-white">
                        {member.name.charAt(0)}
                      </div>
                      <div>
                        <p className="font-medium text-gray-100">
                          {member.name}
                        </p>
                        <p className="text-sm text-gray-400">{member.email}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-300 capitalize">
                        {member.role?.replace('-', ' ')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
