package com.gigigenie.domain.favorite.service;

import com.gigigenie.domain.favorite.dto.FavoriteRequestDTO;
import com.gigigenie.domain.favorite.entity.Favorite;
import com.gigigenie.domain.favorite.repository.FavoriteRepository;
import com.gigigenie.domain.member.entity.Member;
import com.gigigenie.domain.member.repository.MemberRepository;
import com.gigigenie.domain.product.entity.Product;
import com.gigigenie.domain.product.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Transactional
@Slf4j
@RequiredArgsConstructor
@Service
public class FavoriteService {
    private final FavoriteRepository favoriteRepository;
    private final MemberRepository memberRepository;
    private final ProductRepository productRepository;

    public List<Integer> list(Integer memberId) {
        Member member = memberRepository.findById(memberId)
                .orElseThrow(() -> new RuntimeException("Member not found"));
        List<Favorite> favorites = favoriteRepository.findByMember(member);
        if (favorites.isEmpty()) {
            return List.of();
        }
        return favorites.stream()
                .map(favorite -> favorite.getProduct().getId())
                .toList();
    }

    public void addFavorite(FavoriteRequestDTO request) {
        Optional<Member> optionalMember = memberRepository.findById(request.getMemberId());
        Optional<Product> optionalProduct = productRepository.findById(request.getProductId());

        if (optionalMember.isEmpty() || optionalProduct.isEmpty()) {
            log.warn("즐겨찾기 추가 실패 : memberId={}, productId={}",
                    request.getMemberId(), request.getProductId());
            return;
        }

        Member member = optionalMember.get();
        Product product = optionalProduct.get();

        List<Favorite> existingFavorites = favoriteRepository.findByMember(member);
        boolean alreadyExists = existingFavorites.stream()
                .anyMatch(fav -> fav.getProduct().getId().equals(product.getId()));

        if (alreadyExists) {
            log.info("이미 즐겨찾기에 존재함: memberId={}, productId={}", request.getMemberId(), request.getProductId());
            return;
        }

        favoriteRepository.save(new Favorite(product, member));
    }

    public void deleteFavorite(FavoriteRequestDTO request) {
        Optional<Member> optionalMember = memberRepository.findById(request.getMemberId());
        Optional<Product> optionalProduct = productRepository.findById(request.getProductId());

        if (optionalMember.isEmpty() || optionalProduct.isEmpty()) {
            log.warn("즐겨찾기 삭제 요청 실패 : memberId={}, productId={}",
                    request.getMemberId(), request.getProductId());
            return;
        }

        Member member = optionalMember.get();
        Product product = optionalProduct.get();

        favoriteRepository.deleteByProductAndMember(product, member);
    }
}
