# Architecture

```mermaid
flowchart LR
  A[Hugging Face mirror: prices and dividends] -->|sha256 check| B[ingest.py]
  B --> C[data.py: daily total returns]
  C --> D[analysis.py: market model per stock, estimation days -260 to -21]
  D --> E[analysis.py: abnormal returns, CARs, Brown-Warner t, US vs foreign groups]
  C --> F[analysis.py: buy-and-hold returns vs SPY at 63, 126, 250 days]
  E & F --> G[pipeline.py: metrics.json, CSV, figures]
```

Modules: `ingest.py`, `data.py`, `analysis.py`, `figures.py`, `pipeline.py`. Tests: `tests/test_core.py` (market-model recovery, CAR isolates a jump, estimation window excludes the event, BHAR definition).
