import { useState } from 'react'
import { Risk } from '@/types'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'

interface RiskHeatmapProps {
  risks: Risk[]
}

export const RiskHeatmap = ({ risks }: RiskHeatmapProps) => {
  const [selectedCell, setSelectedCell] = useState<{ likelihood: number; impact: number } | null>(null)
  const [hoveredCell, setHoveredCell] = useState<{ likelihood: number; impact: number } | null>(null)

  // Group risks by (likelihood, impact)
  const heatmapData: Record<string, Risk[]> = {}
  risks.forEach((risk) => {
    const key = `${risk.probability}-${risk.impact}`
    if (!heatmapData[key]) {
      heatmapData[key] = []
    }
    heatmapData[key].push(risk)
  })

  // Get max count for gradient calculation
  const maxCount = Math.max(...Object.values(heatmapData).map((risks) => risks.length), 1)

  const getBackgroundColor = (likelihood: number, impact: number): string => {
    const key = `${likelihood}-${impact}`
    const count = heatmapData[key]?.length || 0

    if (count === 0) return 'bg-white'

    const intensity = count / maxCount
    if (intensity > 0.75) return 'bg-red-500'
    if (intensity > 0.5) return 'bg-orange-400'
    if (intensity > 0.25) return 'bg-yellow-300'
    return 'bg-yellow-100'
  }

  const getRisksForCell = (likelihood: number, impact: number): Risk[] => {
    return heatmapData[`${likelihood}-${impact}`] || []
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <h2 className="font-semibold text-gray-900">Risk Heatmap</h2>
          <p className="text-xs text-gray-500">Likelihood (horizontal) × Impact (vertical)</p>
        </CardHeader>
        <CardBody>
          <div className="flex gap-4">
            {/* Y-axis labels (Impact) */}
            <div className="flex flex-col-reverse justify-between pr-2 text-xs font-medium text-gray-600">
              <span>5</span>
              <span>4</span>
              <span>3</span>
              <span>2</span>
              <span>1</span>
            </div>

            {/* Heatmap grid */}
            <div className="flex-1">
              <div className="grid gap-1" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
                {/* Grid cells */}
                {Array.from({ length: 5 }).map((_, impactIdx) => {
                  const impact = 5 - impactIdx
                  return Array.from({ length: 5 }).map((_, likelihoodIdx) => {
                    const likelihood = likelihoodIdx + 1
                    const cellRisks = getRisksForCell(likelihood, impact)
                    const isHovered =
                      hoveredCell?.likelihood === likelihood && hoveredCell?.impact === impact
                    const isSelected =
                      selectedCell?.likelihood === likelihood && selectedCell?.impact === impact

                    return (
                      <div
                        key={`${likelihood}-${impact}`}
                        className={`
                          aspect-square rounded-lg border-2 flex items-center justify-center cursor-pointer
                          transition-all duration-200
                          ${getBackgroundColor(likelihood, impact)}
                          ${isHovered ? 'border-gray-900 shadow-lg scale-105' : 'border-gray-300'}
                          ${isSelected ? 'ring-4 ring-brand-mid' : ''}
                        `}
                        onMouseEnter={() => setHoveredCell({ likelihood, impact })}
                        onMouseLeave={() => setHoveredCell(null)}
                        onClick={() =>
                          setSelectedCell(
                            isSelected ? null : { likelihood, impact }
                          )
                        }
                        title={
                          cellRisks.length > 0
                            ? cellRisks.map((r) => r.title).join(', ')
                            : 'No risks'
                        }
                      >
                        <span className="text-sm font-bold text-white drop-shadow">
                          {cellRisks.length}
                        </span>
                      </div>
                    )
                  })
                })}
              </div>

              {/* X-axis labels (Likelihood) */}
              <div className="flex justify-between mt-2 text-xs font-medium text-gray-600">
                <span>1</span>
                <span>2</span>
                <span>3</span>
                <span>4</span>
                <span>5</span>
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="mt-6 flex gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-white border border-gray-300 rounded" />
              <span>0 risks</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-100 rounded" />
              <span>Low</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-300 rounded" />
              <span>Medium</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-orange-400 rounded" />
              <span>High</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded" />
              <span>Critical</span>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Selected Cell Details */}
      {selectedCell && getRisksForCell(selectedCell.likelihood, selectedCell.impact).length > 0 && (
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-gray-900">
              Risks at L={selectedCell.likelihood}, I={selectedCell.impact}
            </h2>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              {getRisksForCell(selectedCell.likelihood, selectedCell.impact).map((risk) => (
                <div key={risk.id} className="flex items-start justify-between gap-4 p-3 border border-gray-200 rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{risk.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{risk.description}</p>
                  </div>
                  <Badge variant={risk.severity}>{risk.riskScore}</Badge>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
