import { useState } from 'react'
import clsx from 'clsx'
import { HelpCircle } from 'lucide-react'

interface SliderProps {
  label: string
  value: number
  onChange: (value: number) => void
  tooltip: string
  error?: string
  readOnly?: boolean
}

export const Slider = ({ label, value, onChange, tooltip, error, readOnly = false }: SliderProps) => {
  const [showTooltip, setShowTooltip] = useState(false)

  const percentage = ((value - 1) / 4) * 100

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-900">{label}</label>
        <div
          className="relative"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          <HelpCircle size={16} className="text-gray-400 cursor-help" />
          {showTooltip && (
            <div className="absolute bottom-full right-0 mb-2 bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10">
              {tooltip}
              <div className="absolute top-full right-2 w-2 h-2 bg-gray-900 transform rotate-45 -translate-y-1" />
            </div>
          )}
        </div>
      </div>

      {readOnly ? (
        // Read-only bar
        <div className="flex items-center gap-3">
          <div className="flex-1 h-8 bg-gray-100 rounded-full overflow-hidden border border-gray-200">
            <div
              className="h-full bg-gradient-to-r from-brand-mid to-brand-dark transition-all"
              style={{ width: `${percentage}%` }}
            />
          </div>
          <span className="text-sm font-semibold text-gray-900 min-w-6">{value}</span>
        </div>
      ) : (
        // Interactive slider
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="1"
            max="5"
            value={value}
            onChange={(e) => onChange(parseInt(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #e5e7eb 0%, #2E75B6 ${percentage}%, #e5e7eb ${percentage}%, #e5e7eb 100%)`,
            }}
          />
          <span className="text-lg font-bold text-brand-mid min-w-6">{value}</span>
        </div>
      )}

      {/* Scale labels */}
      <div className="flex justify-between text-xs text-gray-500">
        <span>1</span>
        <span>2</span>
        <span>3</span>
        <span>4</span>
        <span>5</span>
      </div>

      {error && <p className="text-sm text-risk-critical">{error}</p>}
    </div>
  )
}

interface ScorePreviewProps {
  likelihood: number
  impact: number
  velocity: number
  detectability: number
}

export const ScorePreview = ({ likelihood, impact, velocity, detectability }: ScorePreviewProps) => {
  const raw = likelihood * impact * velocity * detectability
  const normalized = Math.round((raw / 625) * 100)
  const score = Math.min(100, normalized)

  const getSeverity = (s: number): { band: string; color: string; icon: string; hint: string } => {
    if (s >= 75) return { band: 'CRITICAL', color: 'bg-risk-critical', icon: '🔴', hint: 'IMMEDIATE mitigation required' }
    if (s >= 50) return { band: 'HIGH', color: 'bg-risk-high', icon: '🟠', hint: 'HIGH risk — urgent mitigation planning' }
    if (s >= 25) return { band: 'MEDIUM', color: 'bg-risk-medium', icon: '🟡', hint: 'MEDIUM risk — plan mitigations' }
    return { band: 'LOW', color: 'bg-risk-low', icon: '🟢', hint: 'LOW risk — monitor' }
  }

  const severity = getSeverity(score)

  return (
    <div className={`${severity.color} rounded-lg p-6 text-white space-y-4 sticky top-6`}>
      <div>
        <p className="text-sm opacity-90 mb-2">Live Score Preview</p>
        <div className="flex items-baseline gap-2">
          <span className="text-5xl font-bold">{score}</span>
          <span className="text-sm opacity-75">/100</span>
        </div>
      </div>

      <div className="h-2 bg-white/30 rounded-full overflow-hidden">
        <div
          className="h-full bg-white transition-all"
          style={{ width: `${score}%` }}
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{severity.icon}</span>
          <span className="font-bold text-lg">{severity.band}</span>
        </div>
        <p className="text-sm opacity-90">{severity.hint}</p>
      </div>

      <div className="text-xs opacity-75 space-y-1 pt-3 border-t border-white/20">
        <p>Calculation: ({likelihood} × {impact} × {velocity} × {detectability}) / 625</p>
        <p>Raw: {raw} → Normalized: {normalized}</p>
      </div>
    </div>
  )
}
