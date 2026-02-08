import { Card, CardHeader, CardTitle, CardContent } from './ui/card'
import { Hash, Network, BarChart3 } from 'lucide-react'

interface StatsCardProps {
  title: string;
  value?: string;
  items?: string[];
}

export default function StatsCard({ title, value, items }: StatsCardProps) {
  const getIcon = (title: string) => {
    if (title.includes('Total Blocks')) return <Hash className="w-5 h-5 text-accent-cyan" />
    if (title.includes('Subnets')) return <Network className="w-5 h-5 text-accent-cyan" />
    if (title.includes('Ports')) return <BarChart3 className="w-5 h-5 text-accent-cyan" />
    return null
  }

  return (
    <Card className="bg-background-secondary border-border shadow-lg hover:shadow-xl transition-shadow">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-foreground flex items-center gap-2">
          {getIcon(title)}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {value && (
          <p className="text-3xl font-bold text-accent-cyan">{value}</p>
        )}
        {items && (
          <ul className="space-y-2">
            {items.map((item, index) => (
              <li key={index} className="text-sm text-foreground-secondary font-mono">
                {item}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}