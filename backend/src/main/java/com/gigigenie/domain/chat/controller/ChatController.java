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
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @PostMapping("/ask")
    public Mono<AnswerResponseDTO> getAnswer(@RequestBody QuestionRequestDTO dto, @RequestHeader(value = "Authorization", required = false) String authHeader) {
        log.info("Received chat question request");
        return chatService.getAnswer(dto, authHeader);
    }

    @GetMapping("/history")
    public ResponseEntity<List<QueryHistoryDTO>> getChatHistory(@RequestParam Long productId) {
        log.info("Received request to get chat history for product: {}", productId);
        List<QueryHistoryDTO> histories = chatService.getChatHistory(productId);
        log.info("Returning {} chat history records for product: {}", histories.size(), productId);
        return ResponseEntity.ok(histories);
    }
}

