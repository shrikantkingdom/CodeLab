package com.derai.extraction.controller;

import com.derai.extraction.model.ExtractionRequest;
import com.derai.extraction.model.ExtractionResponse;
import com.derai.extraction.service.PdfBoxExtractorService;
import com.derai.extraction.service.PdfExtractorService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Base64;
import java.util.Map;

/**
 * REST controller for PDF extraction.
 * Accepts base64-encoded PDF content and returns extracted text + structured data.
 */
@RestController
@RequestMapping("/extract")
public class ExtractionController {

    private static final Logger log = LoggerFactory.getLogger(ExtractionController.class);

    private final PdfExtractorService primaryExtractor;
    private final PdfBoxExtractorService pdfBoxExtractor;

    @Value("${extraction.max-file-size:52428800}")
    private long maxFileSize;

    public ExtractionController(
            PdfExtractorService primaryExtractor,
            PdfBoxExtractorService pdfBoxExtractor) {
        this.primaryExtractor = primaryExtractor;
        this.pdfBoxExtractor = pdfBoxExtractor;
    }

    /**
     * Extract content from a PDF document.
     *
     * @param request Contains base64-encoded PDF and optional engine selection
     * @return Extracted text, structured data, and metadata
     */
    @PostMapping("/pdf")
    public ResponseEntity<ExtractionResponse> extractPdf(@Valid @RequestBody ExtractionRequest request) {
        long start = System.currentTimeMillis();

        // Decode base64 PDF content
        byte[] pdfBytes;
        try {
            pdfBytes = Base64.getDecoder().decode(request.getPdfContent());
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(
                    ExtractionResponse.builder()
                            .success(false)
                            .error("Invalid base64-encoded PDF content")
                            .build()
            );
        }

        // Validate file size
        if (pdfBytes.length > maxFileSize) {
            return ResponseEntity.badRequest().body(
                    ExtractionResponse.builder()
                            .success(false)
                            .error("PDF exceeds maximum file size of " + maxFileSize + " bytes")
                            .build()
            );
        }

        // Select extraction engine
        PdfExtractorService extractor = selectEngine(request.getEngine());
        log.info("Extracting PDF ({} bytes) with engine: {}", pdfBytes.length, extractor.getEngineName());

        try {
            Map<String, Object> result = extractor.extract(pdfBytes);
            long elapsed = System.currentTimeMillis() - start;

            @SuppressWarnings("unchecked")
            Map<String, Object> extractedData = (Map<String, Object>) result.getOrDefault("extractedData", Map.of());

            return ResponseEntity.ok(
                    ExtractionResponse.builder()
                            .rawText((String) result.get("rawText"))
                            .extractedData(extractedData)
                            .pageCount((int) result.getOrDefault("pageCount", 0))
                            .engineUsed(extractor.getEngineName())
                            .success(true)
                            .extractionTimeMs(elapsed)
                            .build()
            );
        } catch (Exception e) {
            long elapsed = System.currentTimeMillis() - start;
            log.error("Extraction failed: {}", e.getMessage());
            return ResponseEntity.internalServerError().body(
                    ExtractionResponse.builder()
                            .success(false)
                            .error(e.getMessage())
                            .engineUsed(extractor.getEngineName())
                            .extractionTimeMs(elapsed)
                            .build()
            );
        }
    }

    /**
     * Select extraction engine based on request parameter.
     */
    private PdfExtractorService selectEngine(String engine) {
        if ("pdfbox".equalsIgnoreCase(engine)) {
            return pdfBoxExtractor;
        }
        // Default: primary (Pegbox with PDFBox fallback)
        return primaryExtractor;
    }
}
