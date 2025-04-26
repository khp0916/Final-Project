package com.gigigenie.domain.chat.service;

import com.gigigenie.config.WebClientConfig;
import com.gigigenie.domain.chat.entity.LangchainCollection;
import com.gigigenie.domain.chat.entity.LangchainEmbedding;
import com.gigigenie.domain.chat.repository.LangchainCollectionRepository;
import com.gigigenie.domain.chat.repository.LangchainEmbeddingRepository;
import com.gigigenie.domain.product.entity.Category;
import com.gigigenie.domain.product.entity.Product;
import com.gigigenie.domain.product.repository.CategoryRepository;
import com.gigigenie.domain.product.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.Map;

@Slf4j
@RequiredArgsConstructor
@Service
public class PdfService {

    private final WebClientConfig webClientConfig;
    private final CategoryRepository categoryRepository;
    private final ProductRepository productRepository;
    private final LangchainCollectionRepository collectionRepository;
    private final LangchainEmbeddingRepository embeddingRepository;

    @Transactional
    public Map<String, Object> processPdf(MultipartFile file, Integer categoryId, int chunkSize, int chunkOverlap, String name) {
        // 카테고리와 제품 정보 저장
        Category category = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new RuntimeException("Category not found"));

        Product product = Product.builder()
                .category(category)
                .modelName(name)
                .createdAt(LocalDateTime.now())
                .build();

        productRepository.save(product);

        // FastAPI로 PDF 처리 요청
        Map<String, Object> fastApiResponse = webClientConfig.webClient()
                .post()
                .uri("/api/upload")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData("file", file.getResource())
                        .with("category_id", categoryId)
                        .with("name", name)
                        .with("product_id", product.getId())
                        .with("chunk_size", chunkSize)
                        .with("chunk_overlap", chunkOverlap))
                .retrieve()
                .bodyToMono(Map.class)
                .block();

        if (fastApiResponse == null) {
            throw new RuntimeException("FastAPI 응답이 null입니다.");
        }

        // FastAPI 응답에서 컬렉션 정보 추출
        String collectionName = (String) fastApiResponse.get("collection_name");
        String collectionUuid = (String) fastApiResponse.get("collection_uuid");

        // 컬렉션 정보 저장
        LangchainCollection collection = LangchainCollection.builder()
                .uuid(java.util.UUID.fromString(collectionUuid))
                .name(collectionName)
                .cmetadata(Map.of(
                        "product_id", product.getId(),
                        "model_name", product.getModelName(),
                        "created_at", product.getCreatedAt().toString()
                ))
                .build();
        collectionRepository.save(collection);

        return Map.of(
                "status", "success",
                "collection_name", collectionName,
                "collection_uuid", collectionUuid,
                "chunks_saved", fastApiResponse.get("chunks_saved")
        );
    }
}
