package com.derai.extraction.model;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request body for PDF extraction.
 * Accepts base64-encoded PDF content.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExtractionRequest {

    /** Base64-encoded PDF content. */
    @NotBlank(message = "pdfContent is required")
    private String pdfContent;

    /** Extraction engine to use: "pegbox" or "pdfbox". Defaults to configured default. */
    private String engine;
}
