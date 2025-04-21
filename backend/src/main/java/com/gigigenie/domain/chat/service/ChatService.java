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

import java.util.Collections;
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
        log.info("=== Sending Question to FastAPI ===");
        log.info("Raw DTO: {}", dto);
        log.info("Auth Header: {}", authHeader);
        
        // JWT 토큰에서 user_id 추출
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            try {
                String token = authHeader.substring(7);
                Map<String, Object> claims = jwtUtil.validateToken(token);
                Integer userId = (Integer) claims.get("id");
                dto.setUser_id(userId);
                log.info("Extracted user_id from JWT: {}", userId);
                log.info("Updated DTO with user_id: {}", dto);
            } catch (Exception e) {
                log.warn("Failed to process JWT token: {}", e.getMessage());
            }
        } else {
            log.info("No valid auth header found");
        }
        
        log.info("Sending request to FastAPI with body: {}", dto);
        
        return webClient.post()
                .uri("/api/chat/ask")
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .map(res -> {
                    log.info("=== Received Answer from FastAPI ===");
                    log.info("Response: {}", res);
                    String answer = (String) res.get("answer");
                    
                    if (authHeader != null && authHeader.startsWith("Bearer ")) {
                        try {
                            String token = authHeader.substring(7);
                            Map<String, Object> claims = jwtUtil.validateToken(token);
                            Integer userId = (Integer) claims.get("id");
                            
                            Member member = memberRepository.findById(userId)
                                    .orElseThrow(() -> new RuntimeException("Member not found"));
                            
                            String productIdStr = dto.getCollection_name().replace("product_", "").replace("_embeddings", "");
                            Long productId;
                            try {
                                productId = Long.parseLong(productIdStr);
                            } catch (NumberFormatException e) {
                                log.error("Invalid product ID format: {}", productIdStr);
                                throw new RuntimeException("Invalid product ID format");
                            }
                            
                            QueryHistory queryHistory = new QueryHistory();
                            long currentTime = System.currentTimeMillis();
                            long nanoTime = System.nanoTime() % 1000;
                            queryHistory.setQueryId(currentTime * 1000 + nanoTime);
                            queryHistory.setProductId(productId);
                            queryHistory.setMemberId(member.getMemberId());
                            queryHistory.setQueryText(dto.getQuery());
                            queryHistory.setResponseText(answer);
                            queryHistory.setQueryTime(currentTime);
                            queryHistoryRepository.save(queryHistory);
                            
                            log.info("Query history saved for user: {}, product: {}", userId, productId);
                        } catch (Exception e) {
                            log.error("Failed to save query history: {}", e.getMessage());
                            // 채팅 기록 저장 실패는 전체 프로세스를 중단시키지 않음
                        }
                    }
                    
                    return new AnswerResponseDTO(answer);
                });
    }

    @Transactional(readOnly = true)
    public List<QueryHistoryDTO> getChatHistory(Long productId, Long userId) {
        if (userId == null) {
            log.warn("User ID is required for chat history");
            return Collections.emptyList();
        }

        log.info("Fetching chat history for product: {}, user: {}", productId, userId);
        List<QueryHistory> histories = queryHistoryRepository
                .findByProductIdAndMemberIdOrderByQueryTimeDesc(productId, userId);

        // 최근 10개만 반환
        List<QueryHistory> recentHistory = histories.stream()
            .limit(10)
            .collect(Collectors.toList());

        log.info("Found {} chat history records for product: {}, user: {}",
                recentHistory.size(), productId, userId);
        return recentHistory.stream()
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

