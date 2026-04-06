package com.derai.extraction.service;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.io.IOException;
import java.io.InputStream;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class PdfBoxExtractorServiceTest {

    @Autowired
    private PdfBoxExtractorService pdfBoxExtractor;

    @Test
    void engineNameIsPdfbox() {
        assertEquals("pdfbox", pdfBoxExtractor.getEngineName());
    }

    @Test
    void extractThrowsForInvalidPdf() {
        byte[] invalidPdf = "not a pdf".getBytes();
        assertThrows(RuntimeException.class, () -> pdfBoxExtractor.extract(invalidPdf));
    }
}
