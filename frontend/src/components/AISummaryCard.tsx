import { useState } from 'react'
import { Button } from './ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog'
import { Brain, Loader2 } from 'lucide-react'

interface AISummaryCardProps {
  summary: string;
  onSummaryUpdate: (summary: string, tokens: { input: number; output: number }) => void;
}

// Helper to format AI summary for readability
const formatSummary = (text: string) => {
  const lines = text.split('\n')
  return lines.map((line, index) => {
    if (line.startsWith('-') || line.startsWith('•')) {
      return <li key={index} className="ml-4">{line.substring(1).trim()}</li>
    }
    if (line.includes(':')) {
      const [key, value] = line.split(':', 2)
      return (
        <p key={index}>
          <strong>{key.trim()}:</strong> {value.trim()}
        </p>
      )
    }
    return <p key={index}>{line}</p>
  })
}

export default function AISummaryCard({ summary, onSummaryUpdate }: AISummaryCardProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [open, setOpen] = useState(false)

  const generateSummary = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/ai-summary', { method: 'POST' })
      const data = await response.json()
      if (data.error) {
        onSummaryUpdate(`Error: ${data.error}`, { input: 0, output: 0 })
      } else {
        onSummaryUpdate(data.summary, data.tokens)
        setOpen(true) // Open modal on success
      }
    } catch (error) {
      onSummaryUpdate('Failed to generate summary. Please try again.', { input: 0, output: 0 })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          onClick={generateSummary}
          disabled={isLoading}
          className="bg-accent-cyan hover:bg-accent-cyan/80 text-black font-semibold"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Brain className="w-4 h-4 mr-2" />
              Generate AI Summary
            </>
          )}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-accent-cyan" />
            AI-Powered Analysis
          </DialogTitle>
          <DialogDescription>
            Detailed insights based on recent firewall activity.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {formatSummary(summary)}
        </div>
      </DialogContent>
    </Dialog>
  )
}