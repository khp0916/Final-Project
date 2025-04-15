package com.gigigenie.domain.chat.controller;

import com.gigigenie.domain.chat.dto.AnswerResponseDTO;
import com.gigigenie.domain.chat.dto.QuestionRequestDTO;
import com.gigigenie.domain.chat.dto.QueryHistoryDTO;
import com.gigigenie.domain.chat.service.ChatService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.util.List;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;

    @PostMapping("/ask")
    public Mono<ResponseEntity<AnswerResponseDTO>> getAnswer(
            @RequestBody QuestionRequestDTO dto,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        log.info("=== Received Question Request ===");
        log.info("DTO: {}", dto);
        log.info("Auth Header: {}", authHeader);

        return chatService.getAnswer(dto, authHeader)
                .map(answer -> {
                    log.info("=== Sending Answer Response ===");
                    log.info("Answer: {}", answer);
                    return ResponseEntity.ok(answer);
                });
    }

    @GetMapping("/history")
    public ResponseEntity<List<QueryHistoryDTO>> getChatHistory(
            @RequestParam Long productId,
            @RequestParam Long userId) {
        log.info("=== Received Chat History Request ===");
        log.info("ProductId: {}, UserId: {}", productId, userId);
        
        if (userId == null) {
            log.warn("User ID is required for chat history");
            return ResponseEntity.badRequest().build();
        }
        
        List<QueryHistoryDTO> history = chatService.getChatHistory(productId, userId);
        log.info("=== Sending Chat History Response ===");
        log.info("History size: {}", history.size());
        
        return ResponseEntity.ok(history);
    }
}

