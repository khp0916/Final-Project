package com.gigigenie.domain.product.service;

import com.gigigenie.domain.product.dto.AiSearchRequestDTO;
import com.gigigenie.domain.product.dto.AiSearchResponseDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
@Slf4j
public class AiSearchService {
    private final WebClient webClient;

    public AiSearchResponseDTO searchProducts(String query) {
        log.info("Searching products with query: {}", query);

        AiSearchRequestDTO request = AiSearchRequestDTO.builder()
                .query(query)
                .collectionName("products")
                .topK(3)
                .build();

        return webClient.post()
                .uri("/product/ai-search")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(AiSearchResponseDTO.class)
                .doOnSuccess(response -> log.info("Received search results: {} products", response.getProducts().size()))
                .doOnError(error -> log.error("Error searching products: {}", error.getMessage()))
                .block();
    }
} 