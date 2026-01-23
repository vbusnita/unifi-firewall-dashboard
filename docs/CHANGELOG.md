## 2026-01-22
- Feature 1 & 2 complete: Graylog fetch + parsing (100% match rate on real logs)
- Added unit tests (pytest) for fetch/parse
- Feature 3 baseline: AI summary without normalizer
  - Tokens: 6,169 in / 300 out
  - Est cost per call: ~$0.0014
  - Console per-key increment: $0.0019 (3 requests)