package com.gigigenie.domain.chat.repository;

import com.gigigenie.domain.chat.entity.QueryHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface QueryHistoryRepository extends JpaRepository<QueryHistory, Long> {
    List<QueryHistory> findAllByOrderByQueryTimeDesc();
    List<QueryHistory> findByProductIdOrderByQueryTimeDesc(Long productId);
} 