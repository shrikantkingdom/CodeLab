# Future Enhancements — DERAI Roadmap

## Short-Term (Next Sprint)

### 1. Pre-Processing Pipeline for OCR
Add image enhancement before OCR:
- Deskewing (straighten tilted scans)
- Denoising (remove speckles)
- Binarization (convert grayscale → B&W for better OCR)
- Resolution upscaling (super-resolution for low-DPI faxes)

### 2. Background Job Queue
Replace synchronous batch processing with Celery + Redis:
```
POST /process-batch → returns job_id immediately
GET /jobs/{job_id} → returns progress + partial results
WebSocket /ws/jobs/{job_id} → real-time progress stream
```

### 3. Redis Caching Layer
Cache comparison results and frequently accessed DB records:
- TTL: 15 minutes for comparison results
- TTL: 1 hour for DB records (financial data changes slowly)
- Cache key: `{account}:{doc_type}:{date_range}`

### 4. Enhanced Table Extraction
Dedicated table extraction for financial statements:
- Camelot (Python) for lattice-based tables
- Azure Layout model for complex tables
- Custom post-processing for financial number alignment

---

## Medium-Term (Next Quarter)

### 5. OAuth2 / JWT Authentication
Replace API key auth with proper OAuth2:
- Azure AD integration for enterprise SSO
- JWT tokens with role-based access (admin, analyst, viewer)
- Token refresh and expiry handling
- Audit trail for all API calls

### 6. Multi-Tenant Support
Support multiple client organizations:
- Tenant-scoped API keys
- Isolated database schemas per tenant
- Per-tenant extraction configuration
- Usage metering and billing

### 7. Automated Confidence Scoring
ML model trained on historical comparison results:
- Input: extraction confidence + field similarity scores
- Output: probability that comparison is correct
- Auto-approve high-confidence matches, flag low-confidence for human review

### 8. Document Template Learning
AI learns expected layouts for each document source:
- After processing 50+ documents from same source → build template
- Use template to improve field extraction accuracy
- Alert when document layout changes unexpectedly

---

## Long-Term (Next Year)

### 9. Full ML Pipeline
Replace rule-based comparison with ML:
- NER (Named Entity Recognition) for field extraction
- Transformer-based document understanding (LayoutLM)
- Self-improving accuracy through human feedback loop

### 10. Mobile App
React Native companion app for field staff:
- Camera capture of physical documents
- Real-time OCR processing on-device
- Push notifications for comparison results

### 11. Audit & Compliance Module
Full audit trail for financial regulation:
- Immutable log of every document processed
- Version history for all comparison results
- Compliance reports for regulators
- SOX/SOC2 compliance documentation

### 12. Multi-Cloud Deployment
Support AWS, Azure, GCP equally:
- Terraform modules for each cloud
- Cloud-agnostic storage (S3/Blob/GCS)
- Cloud-agnostic OCR (Textract/Doc AI/Vision AI)
