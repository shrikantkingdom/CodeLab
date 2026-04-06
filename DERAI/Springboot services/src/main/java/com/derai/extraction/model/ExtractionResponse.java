package com.derai.extraction.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Response body for PDF extraction results.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExtractionResponse {

    /** Raw extracted text from the PDF. */
    private String rawText;

    /** Structured data extracted from the PDF. */
    private Map<String, Object> extractedData;

    /** Number of pages in the PDF. */
    private int pageCount;

    /** Engine used for extraction. */
    private String engineUsed;

    /** Whether extraction was successful. */
    private boolean success;

    /** Error message if extraction failed. */
    private String error;

    /** Extraction time in milliseconds. */
    private long extractionTimeMs;
}
