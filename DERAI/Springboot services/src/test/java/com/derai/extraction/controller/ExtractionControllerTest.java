package com.derai.extraction.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class ExtractionControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void healthEndpointReturns200() throws Exception {
        mockMvc.perform(get("/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("healthy"));
    }

    @Test
    void extractPdfReturns401WithoutApiKey() throws Exception {
        mockMvc.perform(post("/extract/pdf")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"pdfContent\": \"dGVzdA==\"}"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void extractPdfReturns400ForInvalidBase64() throws Exception {
        mockMvc.perform(post("/extract/pdf")
                        .header("X-API-Key", "dev-api-key-change-me")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"pdfContent\": \"not-valid-base64!!!\"}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void extractPdfReturns400ForMissingContent() throws Exception {
        mockMvc.perform(post("/extract/pdf")
                        .header("X-API-Key", "dev-api-key-change-me")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"pdfContent\": \"\"}"))
                .andExpect(status().isBadRequest());
    }
}
