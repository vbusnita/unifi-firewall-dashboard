import { Card, CardHeader, CardTitle, CardContent } from './ui/card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp } from 'lucide-react'

interface TimelineChartProps {
  labels: string[];
  data: number[];
}

export default function TimelineChart({ labels, data }: TimelineChartProps) {
  const chartData = labels.map((label, index) => ({
    time: label,
    blocks: data[index] || 0,
  }))

  return (
    <Card className="bg-background-secondary border-border shadow-lg hover:shadow-xl transition-shadow">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-foreground flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-accent-cyan" />
          Blocks Timeline (Last 24h)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
            <XAxis
              dataKey="time"
              stroke="#A3A3A3"
              fontSize={12}
              tick={{ fill: '#A3A3A3' }}
            />
            <YAxis
              stroke="#A3A3A3"
              fontSize={12}
              tick={{ fill: '#A3A3A3' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F0F0F',
                border: '1px solid #262626',
                borderRadius: '8px',
                color: '#FFFFFF',
              }}
              labelStyle={{ color: '#FFFFFF' }}
            />
            <Line
              type="monotone"
              dataKey="blocks"
              stroke="#00D4FF"
              strokeWidth={2}
              dot={{ fill: '#00D4FF', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#00D4FF', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}