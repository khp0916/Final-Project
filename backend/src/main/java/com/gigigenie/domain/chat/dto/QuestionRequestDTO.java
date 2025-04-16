package com.gigigenie.domain.chat.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class QuestionRequestDTO {
    private String query;

    @JsonProperty("collection_name")
    private String collection_name;

    @JsonProperty("top_k")
    private int top_k = 3;

    @JsonProperty("user_id")
    private Integer user_id;

    @JsonProperty("chat_history")
    private List<Map<String, String>> chat_history;
}


