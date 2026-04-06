package com.derai.extraction.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

/**
 * Application-wide configuration properties.
 */
@Configuration
public class AppConfig {

    @Value("${extraction.default-engine:pdfbox}")
    private String defaultEngine;

    @Value("${extraction.max-file-size:52428800}")
    private long maxFileSize;

    public String getDefaultEngine() {
        return defaultEngine;
    }

    public long getMaxFileSize() {
        return maxFileSize;
    }
}
