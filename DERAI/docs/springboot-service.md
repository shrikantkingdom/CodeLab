# Spring Boot Service — In-Depth Documentation

## Overview
The Spring Boot service provides an alternative PDF extraction capability using **Java-based libraries** — primarily Pegbox (proprietary) with Apache PDFBox as fallback. It exposes a single extraction endpoint called by FastAPI when the user selects Java extraction engines.

## Project Structure
```
Springboot services/
├── pom.xml                              # Maven config (Spring Boot 3.x, Java 17)
├── Dockerfile                           # Multi-stage (temurin:17-jdk → temurin:17-jre)
├── src/
│   ├── main/
│   │   ├── java/com/derai/extraction/
│   │   │   ├── Application.java         # @SpringBootApplication entry point
│   │   │   ├── config/
│   │   │   │   ├── AppConfig.java       # Extraction configuration properties
│   │   │   │   └── SecurityConfig.java  # API key filter + Spring Security
│   │   │   ├── controller/
│   │   │   │   ├── ExtractionController.java  # POST /extract/pdf
│   │   │   │   └── HealthController.java      # GET /health
│   │   │   ├── model/
│   │   │   │   ├── ExtractionRequest.java   # base64 pdfContent + engine
│   │   │   │   ├── ExtractionResponse.java  # rawText + extractedData + metadata
│   │   │   │   └── ErrorResponse.java       # Standard error format
│   │   │   ├── service/
│   │   │   │   ├── PdfExtractorService.java     # Interface
│   │   │   │   ├── PegboxExtractorService.java  # @Primary (with fallback)
│   │   │   │   └── PdfBoxExtractorService.java  # Apache PDFBox
│   │   │   └── exception/
│   │   │       └── GlobalExceptionHandler.java  # @ControllerAdvice
│   │   └── resources/
│   │       └── application.yml
│   └── test/
│       └── java/com/derai/extraction/
│           ├── controller/ExtractionControllerTest.java
│           └── service/PdfBoxExtractorServiceTest.java
```

## Key Implementation Details

### 1. Pegbox Integration Strategy
Pegbox is a proprietary/internal library. The integration approach:
- `PegboxExtractorService` is marked `@Primary` — Spring injects it by default
- At startup, it checks classpath for `com.pegbox.PegboxParser`
- If Pegbox JAR is absent → delegates to PDFBox automatically
- If Pegbox fails at runtime → catches exception, falls back to PDFBox
- To install Pegbox locally:
  ```bash
  mvn install:install-file -Dfile=pegbox.jar \
      -DgroupId=com.pegbox -DartifactId=pegbox \
      -Dversion=1.0.0 -Dpackaging=jar
  ```

### 2. API Key Security
- `SecurityConfig` extends Spring Security with a custom `OncePerRequestFilter`
- Validates `X-API-Key` header against configured `app.api-key` property
- Public paths excluded: `/health`, `/actuator/**`, `/swagger-ui/**`
- Returns 401 with JSON error body for invalid/missing keys

### 3. Error Handling
- `@ControllerAdvice` `GlobalExceptionHandler` catches all exceptions
- Validation errors → 400 with field-level messages
- Runtime errors → 500 with generic message (no stack traces leaked)
- Consistent `ErrorResponse` format across all error types

## API Contract

### POST /extract/pdf

**Request:**
```json
{
  "pdfContent": "<base64-encoded PDF>",
  "engine": "pdfbox"  // optional: "pegbox" or "pdfbox"
}
```

**Response (200):**
```json
{
  "rawText": "Account Statement\nAccount: 001-123456...",
  "extractedData": {},
  "pageCount": 3,
  "engineUsed": "pdfbox",
  "success": true,
  "extractionTimeMs": 245
}
```

### GET /health

**Response:**
```json
{
  "status": "healthy",
  "service": "derai-extraction-service",
  "version": "1.0.0",
  "timestamp": "2026-04-05T10:30:00Z"
}
```

## Running Locally

```bash
cd "DERAI/Springboot services"
./mvnw spring-boot:run
# Or: mvn spring-boot:run
```

## Testing

```bash
./mvnw test
```

## Why Spring Boot for PDF Extraction?

| Reason | Detail |
|--------|--------|
| **Pegbox** | Proprietary Java library only available as JAR |
| **PDFBox** | Apache PDFBox is a mature, battle-tested Java PDF library |
| **Java ecosystem** | Rich libraries for document processing (iText, OpenPDF) |
| **Performance** | JVM handles large PDF files with better memory management |
| **Team skills** | Many enterprise teams have Java expertise |
| **Isolation** | Separating extraction into its own service improves resilience |
