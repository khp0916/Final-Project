package com.gigigenie.domain.product.dto;

import lombok.*;

@AllArgsConstructor
@NoArgsConstructor
@Builder
@Setter
@Getter
public class ProductResponseDTO {
    private Integer id;
    private String name;
    private String icon;
}
