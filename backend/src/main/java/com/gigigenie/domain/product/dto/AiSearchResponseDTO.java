package com.gigigenie.domain.product.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiSearchResponseDTO {
    private String query;
    private String answer;
    private List<ProductSearchResult> products;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ProductSearchResult {
        private String productId;
        private String content;
        private Double score;
    }
} 