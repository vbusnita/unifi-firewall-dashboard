import { useEffect, useState } from 'react'
import type { DashboardData } from './types'
import ThreatBanner from './components/ThreatBanner'
import StatsCard from './components/StatsCard'
import AISummaryCard from './components/AISummaryCard'
import TimelineChart from './components/TimelineChart'
import PortsChart from './components/PortsChart'
import AraButton from './components/AraButton'
import TokenFooter from './components/TokenFooter'
import { Button } from './components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/card'
import { RefreshCw, Settings } from 'lucide-react'

declare global {
  interface Window {
    dashboardData: DashboardData;
  }
}

function App() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (window.dashboardData) {
      setData(window.dashboardData)
    } else {
      setError('No data available')
    }
  }, [])

  const handleSummaryUpdate = (summary: string, tokens: { input: number; output: number }) => {
    if (data) {
      setData({ ...data, ai_summary: summary, tokens })
    }
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="bg-background-secondary border border-border rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-bold mb-4">Error Loading Data</h2>
          <p>{error || data?.ai_summary}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-accent-cyan text-black px-4 py-2 rounded hover:bg-accent-cyan/80 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground p-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Threat Banner */}
          <div className="md:col-span-2 lg:col-span-3">
            <ThreatBanner status={data.status} />
          </div>

          {/* Action Buttons */}
          <div className="md:col-span-2 lg:col-span-3">
            <Card className="bg-background-secondary border-border shadow-lg hover:shadow-xl transition-shadow p-6">
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-foreground flex items-center gap-2">
                  <Settings className="w-5 h-5 text-accent-cyan" />
                  Dashboard Controls
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4 justify-center">
                  <AraButton />
                  <Button onClick={() => window.location.reload()} variant="outline" className="border-accent-cyan text-accent-cyan hover:bg-accent-cyan hover:text-black">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh Data
                  </Button>
                  <AISummaryCard summary={data.ai_summary} onSummaryUpdate={handleSummaryUpdate} />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Total Blocks */}
          <StatsCard title="Total Blocks" value={data.total_blocks.toString()} />

          {/* Top Subnets */}
          <StatsCard
            title="Top 5 Source Subnets"
            items={data.top_subnets.map(item => `${item.subnet}: ${item.count}`)}
          />

          {/* Top Ports Chart */}
          <div className="md:col-span-2">
            <PortsChart data={data.top_ports} />
          </div>



          {/* Timeline Chart */}
          <div className="md:col-span-2 lg:col-span-3">
            <TimelineChart labels={data.timeline_labels} data={data.timeline_data} />
          </div>

          {/* Token Footer */}
          <div className="md:col-span-2 lg:col-span-3">
            <TokenFooter tokens={data.tokens} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App