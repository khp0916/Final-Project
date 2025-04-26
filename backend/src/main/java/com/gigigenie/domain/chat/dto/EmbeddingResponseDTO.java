package com.gigigenie.domain.chat.dto;

import lombok.Data;
import java.util.List;

@Data
public class EmbeddingResponseDTO {
    private List<DataItem> data;
    private String model;
    private String object;
    private Usage usage;

    @Data
    public static class DataItem {
        private List<Float> embedding;
        private int index;
        private String object;
    }

    @Data
    public static class Usage {
        private int prompt_tokens;
        private int total_tokens;
    }
//    private List<DataItem> data;
//
//    @Data
//    public static class DataItem {
//        private List<Float> embedding;
//    }

    public List<Float> getEmbedding() {
        return (data != null && !data.isEmpty()) ? data.get(0).getEmbedding() : null;
    }
}
