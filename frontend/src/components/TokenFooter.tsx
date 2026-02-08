interface TokenFooterProps {
  tokens: {
    input: number;
    output: number;
  }
}

export default function TokenFooter({ tokens }: TokenFooterProps) {
  return (
    <div className="text-center text-foreground-tertiary text-sm mt-6">
      Last AI Call: {tokens.input} input / {tokens.output} output tokens
    </div>
  )
}