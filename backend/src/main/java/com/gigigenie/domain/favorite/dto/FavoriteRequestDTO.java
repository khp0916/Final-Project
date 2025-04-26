package com.gigigenie.domain.favorite.dto;

import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
public class FavoriteRequestDTO {
    private Integer memberId;
    private Integer productId;
}
