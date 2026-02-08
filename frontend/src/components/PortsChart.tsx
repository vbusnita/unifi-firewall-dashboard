import { Card, CardHeader, CardTitle, CardContent } from './ui/card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface PortsChartProps {
  data: Record<string, number>;
}

export default function PortsChart({ data }: PortsChartProps) {
  const chartData = Object.entries(data).map(([port, count]) => ({
    port: port.toString(),
    count,
  }))

  return (
    <Card className="bg-background-secondary border-border shadow-md hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-foreground">Top 10 Destination Ports</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
            <XAxis
              type="number"
              stroke="#A3A3A3"
              fontSize={12}
              tick={{ fill: '#A3A3A3' }}
            />
            <YAxis
              type="category"
              dataKey="port"
              stroke="#A3A3A3"
              fontSize={12}
              tick={{ fill: '#A3A3A3' }}
              width={60}
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
            <Bar
              dataKey="count"
              fill="#00D4FF"
              radius={[0, 4, 4, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}