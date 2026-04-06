package com.derai.extraction.service;

import java.util.Map;

/**
 * Interface for PDF extraction engines.
 * Implement this to add a new extraction engine.
 */
public interface PdfExtractorService {

    /**
     * Extract text and structured data from PDF bytes.
     *
     * @param pdfBytes Raw PDF file content
     * @return Map with keys: "rawText" (String), "extractedData" (Map), "pageCount" (int)
     */
    Map<String, Object> extract(byte[] pdfBytes);

    /**
     * @return The name of this extraction engine
     */
    String getEngineName();
}
