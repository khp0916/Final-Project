package com.gigigenie.domain.chat.service;

import com.gigigenie.domain.chat.dto.AnswerResponseDTO;
import com.gigigenie.domain.chat.dto.QuestionRequestDTO;
import com.gigigenie.domain.chat.dto.QueryHistoryDTO;
import com.gigigenie.domain.member.entity.Member;
import com.gigigenie.domain.member.repository.MemberRepository;
import com.gigigenie.domain.chat.entity.QueryHistory;
import com.gigigenie.domain.chat.repository.QueryHistoryRepository;
import com.gigigenie.util.JWTUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class ChatService {

    private final WebClient webClient;
    private final MemberRepository memberRepository;
    private final QueryHistoryRepository queryHistoryRepository;
    private final JWTUtil jwtUtil;

    public Mono<AnswerResponseDTO> getAnswer(QuestionRequestDTO dto, String authHeader) {
        log.info("Sending question to FastAPI - Query: {}, Collection: {}", dto.getQuery(), dto.getCollection_name());
        
        return webClient.post()
                .uri("/api/chat/ask")
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .map(res -> {
                    log.info("Received answer from FastAPI");
                    String answer = (String) res.get("answer");
                    
                    if (authHeader != null && authHeader.startsWith("Bearer ")) {
                        try {
                            String token = authHeader.substring(7);
                            Map<String, Object> claims = jwtUtil.validateToken(token);
                            Integer userId = (Integer) claims.get("id");
                            
                            Member member = memberRepository.findById(userId)
                                    .orElseThrow(() -> new RuntimeException("Member not found"));
                            
                            String productIdStr = dto.getCollection_name().replace("product_", "").replace("_embeddings", "");
                            
                            QueryHistory queryHistory = new QueryHistory();
                            long currentTime = System.currentTimeMillis();
                            long nanoTime = System.nanoTime() % 1000;
                            queryHistory.setQueryId(currentTime * 1000 + nanoTime);
                            queryHistory.setProductId(Long.parseLong(productIdStr));
                            queryHistory.setMemberId(member.getMemberId());
                            queryHistory.setQueryText(dto.getQuery());
                            queryHistory.setResponseText(answer);
                            queryHistory.setQueryTime(currentTime);
                            queryHistoryRepository.save(queryHistory);
                            
                            log.info("Query history saved for user: {}", userId);
                        } catch (Exception e) {
                            log.warn("Failed to process JWT token: {}", e.getMessage());
                        }
                    }
                    
                    return new AnswerResponseDTO(answer);
                });
    }

    @Transactional(readOnly = true)
    public List<QueryHistoryDTO> getChatHistory(Long productId) {
        log.info("Fetching chat history for product: {}", productId);
        List<QueryHistory> histories = queryHistoryRepository.findByProductIdOrderByQueryTimeDesc(productId);
        log.info("Found {} chat history records for product: {}", histories.size(), productId);
        return histories.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    private QueryHistoryDTO convertToDTO(QueryHistory history) {
        return QueryHistoryDTO.builder()
                .queryId(history.getQueryId())
                .productId(history.getProductId())
                .memberId(history.getMemberId())
                .queryText(history.getQueryText())
                .responseText(history.getResponseText())
                .queryTime(history.getQueryTime())
                .formattedQueryTime(history.getFormattedQueryTime())
                .build();
    }
}

