package com.gigigenie.domain.product.controller;

import com.gigigenie.domain.product.dto.ProductResponseDTO;
import com.gigigenie.domain.product.service.ProductService;
import com.gigigenie.domain.product.service.AiSearchService;
import com.gigigenie.domain.product.dto.AiSearchResponseDTO;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RequiredArgsConstructor
@RequestMapping("/api/product")
@RestController
public class ProductController {

    private final ProductService productService;
    private final AiSearchService aiSearchService;

    @Operation(summary = "제품 전체 조회")
    @GetMapping("/list")
    public ResponseEntity<List<ProductResponseDTO>> list() {
        List<ProductResponseDTO> list = productService.list();
        return ResponseEntity.ok(list);
    }

    @PostMapping("/ai-search")
    public ResponseEntity<AiSearchResponseDTO> searchProducts(@RequestBody Map<String, String> request) {
        String query = request.get("query");
        if (query == null || query.trim().isEmpty()) {
            throw new IllegalArgumentException("검색어를 입력해주세요.");
        }

        AiSearchResponseDTO response = aiSearchService.searchProducts(query);
        return ResponseEntity.ok(response);
    }
}
