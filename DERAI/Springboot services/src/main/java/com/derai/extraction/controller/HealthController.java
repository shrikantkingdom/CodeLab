package com.derai.extraction.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

/**
 * Health check endpoint for the extraction service.
 */
@RestController
public class HealthController {

    @Value("${spring.application.name:derai-extraction-service}")
    private String appName;

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "healthy",
                "service", appName,
                "version", "1.0.0",
                "timestamp", Instant.now().toString()
        ));
    }
}
