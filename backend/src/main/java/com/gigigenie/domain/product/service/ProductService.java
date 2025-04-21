package com.gigigenie.domain.product.service;

import com.gigigenie.domain.product.dto.ProductResponseDTO;
import com.gigigenie.domain.product.entity.Product;
import com.gigigenie.domain.product.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@RequiredArgsConstructor
@Service
public class ProductService {

    private final ProductRepository productRepository;

    public List<ProductResponseDTO> list() {
        List<Product> products = productRepository.findAll();
        return products.stream().map(product -> (
                ProductResponseDTO.builder()
                        .id(product.getId())
                        .name(product.getModelName())
                        .icon(product.getCategory().getCategoryIcon())
                        .build())).collect(Collectors.toList());
    }

}
