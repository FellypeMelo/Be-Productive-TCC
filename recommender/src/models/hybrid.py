"""
Hybrid Recommendation Model
Combines content-based and collaborative filtering
"""

import hashlib
from typing import Optional, List, Tuple
import numpy as np
from scipy import sparse

from src.models.content_based import ContentBasedModel
from src.models.collaborative import CollaborativeModel


def _deterministic_component_score(content_id: int, component: str) -> float:
    """Stable placeholder score in [0.3, 0.8] for a model component.

    The content-based and collaborative sub-models are not fitted in this
    build. Previously ``predict`` filled their outputs with ``np.random.rand``,
    which produced a different feed on every call and could not be tested. This
    replaces that noise with a deterministic SHA-256-derived value per
    (content_id, component): same inputs -> same score, spread across the range
    that the old ``rand * 0.5 + 0.3`` used. Replace with real component calls
    once the sub-models are trained.
    """
    digest = hashlib.sha256(f"{component}:{content_id}".encode("utf-8")).digest()
    u = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return 0.3 + u * 0.5


class HybridRecommender:
    """
    Hybrid recommendation model that combines:
    1. Content-based filtering (topic/tag similarity)
    2. Collaborative filtering (user-item interactions via implicit)
    3. Quality score weighting
    
    The combination uses weighted averaging with configurable weights.
    """
    
    def __init__(
        self,
        content_weight: float = 0.4,
        collab_weight: float = 0.4,
        quality_weight: float = 0.2
    ):
        """
        Initialize hybrid model with component weights.
        
        Args:
            content_weight: Weight for content-based scores
            collab_weight: Weight for collaborative filtering scores
            quality_weight: Weight for quality scores
        """
        self.content_weight = content_weight
        self.collab_weight = collab_weight
        self.quality_weight = quality_weight
        
        self.content_model = ContentBasedModel()
        self.collab_model = CollaborativeModel()
        
        # Quality scores cache (content_id -> score)
        self._quality_cache: dict = {}
    
    def fit(
        self,
        user_topic_matrix: sparse.csr_matrix,
        content_topic_matrix: sparse.csr_matrix,
        user_content_interactions: sparse.csr_matrix,
        quality_scores: dict
    ):
        """
        Train the hybrid model.
        
        Args:
            user_topic_matrix: User-topic preferences
            content_topic_matrix: Content-topic associations
            user_content_interactions: User-content interaction matrix
            quality_scores: Dict mapping content_id to quality score
        """
        # Train content-based model
        self.content_model.fit(user_topic_matrix, content_topic_matrix)
        
        # Train collaborative model
        self.collab_model.fit(user_content_interactions)
        
        # Cache quality scores
        self._quality_cache = quality_scores
    
    def predict(
        self,
        user_id: int,
        candidate_ids: List[int],
        category: Optional[str] = None
    ) -> Tuple[List[int], np.ndarray]:
        """
        Generate predictions for a user.
        
        Args:
            user_id: User to recommend for
            candidate_ids: List of candidate content IDs
            category: Optional category filter
        
        Returns:
            Tuple of (content_ids, scores)
        """
        # Component scores. The sub-models are not fitted in this build, so we
        # use deterministic per-content placeholders (documented, reproducible)
        # instead of random noise. In production these become real calls to
        # self.content_model / self.collab_model.
        content_scores = np.array([
            _deterministic_component_score(cid, "content")
            for cid in candidate_ids
        ])
        collab_scores = np.array([
            _deterministic_component_score(cid, "collab")
            for cid in candidate_ids
        ])
        quality_scores = np.array([
            self._quality_cache.get(cid, 0.5)
            for cid in candidate_ids
        ])
        
        # Combine scores
        combined_scores = (
            self.content_weight * content_scores +
            self.collab_weight * collab_scores +
            self.quality_weight * quality_scores
        )
        
        return candidate_ids, combined_scores
    
    def save(self, path: str):
        """Save model to disk"""
        # In production, serialize model components
        pass
    
    def load(self, path: str):
        """Load model from disk"""
        # In production, deserialize model components
        pass
