// Risk-specific components stubs

import { Risk } from '@/types'
import { Card, CardBody } from '@/components/ui/Card'
import { Badge, StatusBadge } from '@/components/ui/Badge'

export const RiskCard = ({ risk }: { risk: Risk }) => (
  <Card className="hover">
    <CardBody>
      <div className="space-y-3">
        <div className="flex justify-between items-start gap-4">
          <h3 className="font-semibold text-gray-900">{risk.title}</h3>
          <Badge variant={risk.severity}>{risk.severity}</Badge>
        </div>
        <p className="text-sm text-gray-600 line-clamp-2">{risk.description}</p>
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>Score: {risk.riskScore}</span>
          <StatusBadge status={risk.status} />
        </div>
      </div>
    </CardBody>
  </Card>
)

export const RiskBadge = ({ severity }: { severity: Risk['severity'] }) => (
  <Badge variant={severity}>{severity}</Badge>
)

export const RiskTable = () => (
  <div className="bg-white rounded-lg p-6">
    <p className="text-gray-500">Risk Table component - to be implemented</p>
  </div>
)

export const RiskHeatmap = () => (
  <div className="bg-white rounded-lg p-6">
    <p className="text-gray-500">Risk Heatmap component - to be implemented</p>
  </div>
)

export const RiskChainGraph = () => (
  <div className="bg-white rounded-lg p-6">
    <p className="text-gray-500">Risk Chain Graph component - to be implemented</p>
  </div>
)
