package com.gigigenie.domain.favorite.controller;

import com.gigigenie.domain.favorite.dto.FavoriteRequestDTO;
import com.gigigenie.domain.favorite.service.FavoriteService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RequiredArgsConstructor
@RequestMapping("/api/favorite")
@RestController
public class FavoriteController {
    private final FavoriteService favoriteService;

    @Operation(summary = "회원별 즐겨찾기 전체 조회")
    @GetMapping("/member")
    public ResponseEntity<List<Integer>> list(
            @Parameter(description = "회원ID(FK)", required = true)
            @RequestParam Integer memberId) {
        List<Integer> ids = favoriteService.list(memberId);
        log.info("즐겨찾기 목록 조회 결과: {}", ids);
        return ResponseEntity.ok(ids);
    }

    @Operation(summary = "즐겨찾기 추가")
    @PostMapping("/add")
    public void addFavorite(@RequestBody FavoriteRequestDTO request) {
        log.info("즐겨찾기 추가 요청: {}", request);
        favoriteService.addFavorite(request);
    }

    @Operation(summary = "즐겨찾기 삭제")
    @PostMapping("/delete")
    public void deleteFavorite(@RequestBody FavoriteRequestDTO request) {
        log.info("즐겨찾기 삭제 요청: {}", request);
        favoriteService.deleteFavorite(request);
    }
}
