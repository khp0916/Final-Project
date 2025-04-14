package com.gigigenie.domain.chat.dto;

import com.gigigenie.domain.chat.entity.QueryHistory;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QueryHistoryDTO {
    private Long queryId;
    private Long productId;
    private Integer memberId;
    private String queryText;
    private String responseText;
    private Long queryTime;
    private String formattedQueryTime;

    public static QueryHistoryDTO fromEntity(QueryHistory entity) {
        return QueryHistoryDTO.builder()
                .queryId(entity.getQueryId())
                .productId(entity.getProductId())
                .memberId(entity.getMemberId())
                .queryText(entity.getQueryText())
                .responseText(entity.getResponseText())
                .queryTime(entity.getQueryTime())
                .formattedQueryTime(entity.getFormattedQueryTime())
                .build();
    }
} 