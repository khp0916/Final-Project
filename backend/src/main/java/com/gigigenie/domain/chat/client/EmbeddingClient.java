package com.gigigenie.domain.chat.client;

import com.gigigenie.domain.chat.dto.EmbeddingResponseDTO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class EmbeddingClient {

    private final WebClient webClient;
    private final String EMBEDDING_API_URL = "https://api.openai.com/v1/embeddings";

    public EmbeddingClient(@Value("${openai.api.key}") String apiKey) {
        this.webClient = WebClient.builder()
                .baseUrl(EMBEDDING_API_URL)
                .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + apiKey)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }

    public List<Float> embed(String input) {
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("input", input);
        requestBody.put("model", "text-embedding-3-small");

        System.out.println("임베딩 요청 주소: " + EMBEDDING_API_URL);

        try {
            return webClient.post()
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(EmbeddingResponseDTO.class)
                    .map(EmbeddingResponseDTO::getEmbedding)
                    .block();
        } catch (WebClientResponseException e) {
            System.out.println("임베딩 API 응답 오류: " + e.getStatusCode());
            System.out.println("응답 바디: " + e.getResponseBodyAsString());
            throw e;
        }
    }
}
