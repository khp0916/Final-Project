package com.gigigenie.domain.chat.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

@Entity
@Table(name = "query_history")
@Getter
@Setter
@NoArgsConstructor
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class QueryHistory {
    @Id
    @Column(name = "query_id")
    private Long queryId;

    @Column(name = "product_id", nullable = false)
    private Long productId;

    @Size(max = 255)
    @NotNull
    @Column(name = "query_text", nullable = false)
    private String queryText;

    @NotNull
    @Column(name = "response_text", nullable = false, columnDefinition = "TEXT")
    private String responseText;

    @NotNull
    @Column(name = "query_time", nullable = false)
    private Long queryTime;

    @NotNull
    @Column(name = "member_id", nullable = false)
    private Integer memberId;

    public String getFormattedQueryTime() {
        LocalDateTime dateTime = LocalDateTime.ofInstant(
            java.time.Instant.ofEpochMilli(queryTime),
            ZoneId.systemDefault()
        );
        return dateTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }
} 