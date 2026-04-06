package com.derai.extraction.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * PDF extraction using Pegbox library (primary engine).
 *
 * NOTE: Pegbox is a proprietary/internal library. This implementation
 * provides the integration point. If Pegbox JAR is not available,
 * the service will delegate to PdfBoxExtractorService as fallback.
 *
 * To install Pegbox locally:
 *   mvn install:install-file -Dfile=pegbox.jar -DgroupId=com.pegbox \
 *       -DartifactId=pegbox -Dversion=1.0.0 -Dpackaging=jar
 */
@Service
@Primary
public class PegboxExtractorService implements PdfExtractorService {

    private static final Logger log = LoggerFactory.getLogger(PegboxExtractorService.class);

    private final PdfBoxExtractorService fallback;
    private boolean pegboxAvailable;

    public PegboxExtractorService(PdfBoxExtractorService fallback) {
        this.fallback = fallback;
        this.pegboxAvailable = checkPegboxAvailability();
    }

    @Override
    public String getEngineName() {
        return pegboxAvailable ? "pegbox" : "pdfbox";
    }

    @Override
    public Map<String, Object> extract(byte[] pdfBytes) {
        if (!pegboxAvailable) {
            log.warn("Pegbox not available — delegating to PDFBox fallback");
            return fallback.extract(pdfBytes);
        }

        try {
            return extractWithPegbox(pdfBytes);
        } catch (Exception e) {
            log.error("Pegbox extraction failed, falling back to PDFBox: {}", e.getMessage());
            return fallback.extract(pdfBytes);
        }
    }

    /**
     * Pegbox extraction implementation.
     * Replace this with actual Pegbox API calls when the library is available.
     */
    private Map<String, Object> extractWithPegbox(byte[] pdfBytes) {
        // TODO: Replace with actual Pegbox library calls
        // Example:
        //   PegboxDocument doc = PegboxParser.parse(pdfBytes);
        //   String text = doc.getText();
        //   Map<String, Object> fields = doc.getStructuredFields();

        log.info("Pegbox extraction — using stub implementation (replace with real Pegbox calls)");

        // For now, delegate to PDFBox as Pegbox is not yet integrated
        Map<String, Object> result = fallback.extract(pdfBytes);
        result.put("engineNote", "Pegbox stub — using PDFBox internally until Pegbox JAR is provided");
        return result;
    }

    /**
     * Check if Pegbox library is available on the classpath.
     */
    private boolean checkPegboxAvailability() {
        try {
            Class.forName("com.pegbox.PegboxParser");
            log.info("Pegbox library detected on classpath");
            return true;
        } catch (ClassNotFoundException e) {
            log.info("Pegbox library not found — will use PDFBox fallback");
            return false;
        }
    }
}
