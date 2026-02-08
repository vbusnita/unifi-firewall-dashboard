import { Card } from './ui/card'
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react'

interface ThreatBannerProps {
  status: {
    level: string;
    color: string;
  }
}

export default function ThreatBanner({ status }: ThreatBannerProps) {
  const getGradient = (level: string) => {
    if (level.includes('High')) return 'bg-gradient-to-r from-red-500 to-red-700'
    if (level.includes('Moderate')) return 'bg-gradient-to-r from-amber-500 to-amber-700'
    if (level.includes('Low')) return 'bg-gradient-to-r from-green-500 to-green-700'
    return 'bg-gradient-to-r from-gray-500 to-gray-700'
  }

  const getIcon = (level: string) => {
    if (level.includes('High')) return <AlertTriangle className="w-8 h-8" />
    if (level.includes('Moderate')) return <Shield className="w-8 h-8" />
    if (level.includes('Low')) return <CheckCircle className="w-8 h-8" />
    return <Shield className="w-8 h-8" />
  }

  return (
    <Card className={`p-6 ${getGradient(status.level)} text-white shadow-lg hover:shadow-xl transition-shadow`}>
      <div className="flex items-center justify-center gap-4">
        {getIcon(status.level)}
        <h1 className="text-3xl font-bold">{status.level}</h1>
      </div>
    </Card>
  )
}