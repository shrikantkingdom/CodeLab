# React UI — In-Depth Documentation

## Overview
The React frontend provides a dashboard for QA analysts and operations users to submit documents for processing, view comparison results, and monitor system health. It communicates exclusively with the FastAPI backend.

## Project Structure
```
React UI/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── Dockerfile                    # Multi-stage (node:20 → nginx:alpine)
├── .env.example
└── src/
    ├── main.tsx                  # Entry point (React Query, MUI Theme)
    ├── App.tsx                   # Router: Dashboard, Process, History
    ├── vite-env.d.ts             # Vite env type declarations
    ├── api/
    │   ├── client.ts             # Axios instance (base URL, API key, interceptors)
    │   └── deraiApi.ts           # API functions (processSingle, processBatch, etc.)
    ├── components/
    │   ├── Layout.tsx            # AppBar + Drawer + Outlet
    │   ├── SingleInputForm.tsx   # Account, document type, engine, dates
    │   └── ComparisonTable.tsx   # Field-by-field results with color coding
    ├── pages/
    │   ├── Dashboard.tsx         # Health status cards, quick start guide
    │   ├── ProcessPage.tsx       # Form + results
    │   └── HistoryPage.tsx       # Past results with account filter
    └── types/
        └── index.ts              # TypeScript types mirroring FastAPI models
```

## Key Implementation Details

### 1. Engine Selector Architecture
The UI groups extraction engines into categories for better UX:

| Category | Engines | Use Case |
|----------|---------|----------|
| **Standard** | PyMuPDF, pdfplumber, Tika | Text-based PDFs (fastest) |
| **Java** | Pegbox, PDFBox | Enterprise Java extraction |
| **OCR** | pytesseract, Azure | Scanned/image PDFs (all pages) |
| **Hybrid** | Hybrid+pytesseract, Hybrid+Azure | Mixed PDFs: text pages + OCR for images |

### 2. React Query for Data Fetching
- Mutations for process-single (no caching, immediate)
- Queries for health check (30s auto-refresh)
- Queries for history (refetch on filter change)

### 3. Material UI Theming
- Primary: Blue (#1565c0) — navigation, actions
- Success: Green (#2e7d32) — match indicators
- Error: Red (#c62828) — mismatch indicators
- Warning: Orange (#ef6c00) — missing field indicators

### 4. Vite Proxy Configuration
In development, `/api` requests are proxied to `http://localhost:8000` — no CORS issues.
In production (Docker), nginx reverse-proxies `/api` to the FastAPI container.

## Component Hierarchy

```
App
├── Layout (AppBar + Drawer navigation)
│   ├── Dashboard
│   │   └── ServiceStatus × 4 (FastAPI, Snowflake, DB2, Spring Boot)
│   ├── ProcessPage
│   │   ├── SingleInputForm
│   │   │   ├── AccountNumber (office + account fields)
│   │   │   ├── DocumentType selector
│   │   │   ├── ExtractionEngine selector (grouped by category)
│   │   │   └── Conditional fields (dates, types per doc type)
│   │   └── ComparisonTable (shown after processing)
│   │       └── FieldComparison rows (color-coded chips)
│   └── HistoryPage
│       ├── Filter bar (account number search)
│       └── ComparisonTable × N (past results)
```

## Running Locally

```bash
cd "DERAI/React UI"
npm install
cp .env.example .env
npm run dev
# Opens on http://localhost:3000
```

## Building for Production

```bash
npm run build
# Output in dist/ — serve with any static file server
```
