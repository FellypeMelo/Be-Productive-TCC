"""
Hybrid Recommendation Model
Combines content-based and collaborative filtering
"""

from typing import Optional, List, Tuple
import numpy as np
from scipy import sparse

from src.models.content_based import ContentBasedModel
from src.models.collaborative import CollaborativeModel


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
        n_candidates = len(candidate_ids)
        
        # Get scores from each model
        # For now, use mock scores (in production, call actual models)
        content_scores = np.random.rand(n_candidates) * 0.5 + 0.3
        collab_scores = np.random.rand(n_candidates) * 0.5 + 0.3
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
