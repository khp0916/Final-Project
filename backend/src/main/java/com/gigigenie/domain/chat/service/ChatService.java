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
        Integer userId = null;
        
        // JWT 토큰에서 user_id 추출
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            try {
                String token = authHeader.substring(7);
                Map<String, Object> claims = jwtUtil.validateToken(token);
                userId = (Integer) claims.get("id");
                dto.setUser_id(userId);
            } catch (Exception e) {
                log.warn("Failed to process JWT token: {}", e.getMessage());
            }
        }

        // 이전 대화 기록 조회
        if (userId != null) {
            String productIdStr = dto.getCollection_name().replace("product_", "").replace("_embeddings", "");
            Long productId = Long.parseLong(productIdStr);
            
            List<QueryHistory> histories = queryHistoryRepository
                    .findByProductIdAndMemberIdOrderByQueryTimeDesc(productId, userId.longValue());
            
            // 최근 5개의 대화만 포함
            List<Map<String, String>> chatHistory = histories.stream()
                    .limit(10)
                    .map(history -> Map.of(
                            "question", history.getQueryText(),
                            "answer", history.getResponseText()
                    ))
                    .collect(Collectors.toList());
            
            dto.setChat_history(chatHistory);
        }
        
        return webClient.post()
                .uri("/api/chat/ask")
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<Map<String, Object>>() {})
                .map(res -> {
                    String answer = (String) res.get("answer");
                    
                    // 응답 저장
                    if (userId != null) {
                        try {
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
                        } catch (Exception e) {
                            log.warn("Failed to save query history: {}", e.getMessage());
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

        log.info("Found {} chat history records for product: {}, user: {}",
                histories.size(), productId, userId);
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

