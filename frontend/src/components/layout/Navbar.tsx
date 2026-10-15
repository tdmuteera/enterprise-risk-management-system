import { Search } from 'lucide-react'
import { AlertsBell } from '@/components/navbar/AlertsBell'

export const Navbar = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-20 md:left-72">
      <div className="h-px w-full bg-gradient-to-r from-transparent via-brand-mid/25 to-transparent" aria-hidden />
      <nav className="flex h-16 items-center justify-between gap-4 border-b border-slate-200/70 bg-white/80 px-4 shadow-[0_8px_30px_-18px_rgba(21,43,82,0.35)] backdrop-blur-xl sm:px-8">
        <div className="flex min-w-0 flex-1 items-center md:pl-0">
          <div className="relative w-full max-w-xl">
            <Search
              className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
              strokeWidth={2}
            />
            <input
              type="search"
              placeholder="Search risks, departments, reports…"
              className="w-full rounded-2xl border border-slate-200/80 bg-surface-muted/80 py-2.5 pl-10 pr-4 text-sm text-slate-800 shadow-inner placeholder:text-slate-400 focus:border-brand-mid/40 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-mid/20"
            />
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 border-l border-slate-200/60 pl-4 sm:gap-3 sm:pl-6">
          <AlertsBell />
        </div>
      </nav>
    </header>
  )
}
