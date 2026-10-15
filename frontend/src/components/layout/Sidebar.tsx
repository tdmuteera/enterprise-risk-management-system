import { useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import clsx from 'clsx'
import {
  Menu,
  X,
  BarChart3,
  AlertCircle,
  Shield,
  Users,
  FileText,
  LogOut,
  Settings,
  LayoutGrid,
  ScrollText,
  Search,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { prefetchSidebarRoute } from '@/lib/prefetchNav'
import type { User } from '@/types'

type UserRole = User['role']

interface NavItem {
  label: string
  href: string
  icon: typeof BarChart3
  roles?: UserRole[]
}

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: BarChart3 },
  { label: 'Risks', href: '/risks', icon: AlertCircle, roles: ['admin', 'risk_officer', 'dept_user', 'data_clerk', 'risk_clerk', 'risk_manager', 'department_head'] },
  { label: 'Departments', href: '/departments', icon: Shield, roles: ['admin', 'risk_officer', 'dept_user', 'data_clerk', 'risk_clerk', 'risk_manager', 'department_head'] },
  { label: 'Alerts', href: '/alerts', icon: AlertCircle },
  { label: 'Reports', href: '/reports', icon: FileText, roles: ['admin', 'risk_officer', 'executive', 'risk_manager', 'department_head'] },
  { label: 'Audit Trail', href: '/audit-trail', icon: ScrollText, roles: ['admin', 'risk_officer', 'risk_manager', 'department_head'] },
  { label: 'Forensic', href: '/forensic', icon: Search, roles: ['admin', 'risk_officer', 'risk_manager', 'department_head'] },
  { label: 'Users', href: '/users', icon: Users, roles: ['admin'] },
]

function routeIsActive(pathname: string, href: string): boolean {
  if (pathname === href) return true
  if (href === '/dashboard') return pathname.startsWith('/dashboard')
  return pathname.startsWith(`${href}/`)
}

export const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false)
  const { pathname } = useLocation()
  const { user, logout } = useAuth()

  const visibleItems = navItems.filter((item) => {
    if (!item.roles) return true
    return user?.role ? item.roles.includes(user.role) : false
  })

  const initials = useMemo(() => {
    const n = user?.name || user?.email || '?'
    const parts = n.split(/\s+/).filter(Boolean)
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
    return n.slice(0, 2).toUpperCase()
  }, [user?.name, user?.email])

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-4 top-4 z-40 flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200/80 bg-white/90 text-slate-700 shadow-nav backdrop-blur-md transition hover:bg-white md:hidden"
        aria-label={isOpen ? 'Close menu' : 'Open menu'}
      >
        {isOpen ? <X size={22} strokeWidth={2} /> : <Menu size={22} strokeWidth={2} />}
      </button>

      <aside
        className={clsx(
          'fixed left-0 top-0 z-30 flex h-screen w-72 flex-col bg-sidebar-gradient text-white shadow-sidebar transition-transform duration-300 ease-out',
          'md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        <div
          className="pointer-events-none absolute inset-0 bg-sidebar-shine opacity-90"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute left-0 top-0 h-full w-px bg-gradient-to-b from-brand-accent/50 via-white/15 to-transparent"
          aria-hidden
        />

        <div className="relative shrink-0 px-5 pb-6 pt-7">
          <div className="flex items-start gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white/10 font-display text-lg font-semibold tracking-tight text-white ring-1 ring-white/15">
              E
            </div>
            <div className="min-w-0 pt-0.5">
              <h1 className="font-display text-lg font-semibold leading-tight tracking-tight text-white">
                ERM Platform
              </h1>
              <p className="mt-0.5 text-[11px] font-medium uppercase tracking-[0.2em] text-brand-accent/90">
                Enterprise risk
              </p>
            </div>
          </div>
        </div>

        <div className="relative mx-4 mb-2 flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          <LayoutGrid className="h-3.5 w-3.5 text-brand-accent" strokeWidth={2} />
          Workspace
        </div>

        <nav className="relative min-h-0 flex-1 overflow-y-auto layout-scrollbar px-3 pb-4">
          {visibleItems.map((item) => {
            const Icon = item.icon
            const active = routeIsActive(pathname, item.href)
            return (
              <Link
                key={item.href}
                to={item.href}
                onMouseEnter={() => prefetchSidebarRoute(item.href, { departmentId: user?.departmentId })}
                onClick={() => setIsOpen(false)}
                className={clsx(
                  'group relative mb-1 flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all duration-200',
                  active
                    ? 'bg-white/[0.12] text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.12)]'
                    : 'text-slate-300 hover:bg-white/[0.06] hover:text-white'
                )}
              >
                <span
                  className={clsx(
                    'absolute left-0 top-1/2 h-8 w-1 -translate-y-1/2 rounded-r-full bg-brand-accent transition-opacity',
                    active ? 'opacity-100' : 'opacity-0 group-hover:opacity-40'
                  )}
                  aria-hidden
                />
                <span
                  className={clsx(
                    'flex h-9 w-9 shrink-0 items-center justify-center rounded-lg transition-colors',
                    active
                      ? 'bg-brand-mid/40 text-white ring-1 ring-white/10'
                      : 'bg-white/5 text-slate-300 group-hover:bg-white/10 group-hover:text-white'
                  )}
                >
                  <Icon size={18} strokeWidth={2} />
                </span>
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="relative mt-auto shrink-0 border-t border-white/10 bg-black/15 px-4 py-4 backdrop-blur-sm">
          <div className="mb-3 flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-mid to-brand-dark font-display text-sm font-semibold text-white ring-1 ring-white/20">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-white">{user?.name || 'User'}</p>
              <p className="truncate text-xs text-slate-400">{user?.email}</p>
              <p className="mt-0.5 text-[10px] font-medium uppercase tracking-wider text-brand-accent/90">
                {user?.role?.replace(/_/g, ' ')}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link
              to="/settings"
              onClick={() => setIsOpen(false)}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-xs font-semibold text-slate-200 transition hover:border-white/20 hover:bg-white/10 hover:text-white"
            >
              <Settings size={15} strokeWidth={2} />
              Settings
            </Link>
            <button
              type="button"
              onClick={logout}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-risk-critical/30 bg-risk-critical/15 px-3 py-2.5 text-xs font-semibold text-red-100 transition hover:bg-risk-critical/25"
            >
              <LogOut size={15} strokeWidth={2} />
              Log out
            </button>
          </div>
        </div>
      </aside>

      {isOpen && (
        <button
          type="button"
          className="fixed inset-0 z-20 bg-slate-900/40 backdrop-blur-[2px] md:hidden"
          aria-label="Close menu overlay"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  )
}
