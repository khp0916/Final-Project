package com.gigigenie.domain.product.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiSearchRequestDTO {
    private String query;
    
    @JsonProperty("collection_name")
    private String collectionName;
    
    @JsonProperty("top_k")
    private Integer topK;
}
