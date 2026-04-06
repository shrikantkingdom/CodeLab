package com.derai.extraction.service;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * PDF extraction using Apache PDFBox.
 * Acts as fallback when Pegbox is unavailable.
 */
@Service
public class PdfBoxExtractorService implements PdfExtractorService {

    private static final Logger log = LoggerFactory.getLogger(PdfBoxExtractorService.class);

    @Override
    public String getEngineName() {
        return "pdfbox";
    }

    @Override
    public Map<String, Object> extract(byte[] pdfBytes) {
        Map<String, Object> result = new HashMap<>();

        try (PDDocument document = Loader.loadPDF(pdfBytes)) {
            PDFTextStripper stripper = new PDFTextStripper();
            String rawText = stripper.getText(document);
            int pageCount = document.getNumberOfPages();

            result.put("rawText", rawText);
            result.put("extractedData", new HashMap<>());
            result.put("pageCount", pageCount);

            log.info("PDFBox extracted {} pages", pageCount);
        } catch (IOException e) {
            log.error("PDFBox extraction failed: {}", e.getMessage());
            throw new RuntimeException("PDF extraction failed: " + e.getMessage(), e);
        }

        return result;
    }
}
