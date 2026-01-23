## AI Summary Cost Comparison (2026-01-22, limit=100)

### Baseline (full logs)
- Logs sent: 100 raw messages
- Input tokens: 12,181
- Output tokens: 291
- Est cost: $0.002582
- Console per-key increment: ~$0.001–$0.002 (part of today's $0.0052)
- Summary quality: Detailed (lists IPs, patterns, HIGH risk due to volume)

### With Normalizer (group by /24 + port + proto)
- Groups created: 9 (from 200 logs)
- Input tokens: 384
- Output tokens: 170
- Est cost: $0.000162
- Savings: **96.8% on input tokens**, **93.7% on total est cost**
- Summary quality: Excellent — identifies dominant port/subnet, coordinated scanning, LOW risk (blocked, no variety)
- Verdict: Normalizer preserves signal, cuts tokens dramatically → **default for production**

Recommendation: Always use normalizer; exclude noise ports like 51413 in future v2.