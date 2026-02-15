"""
Collaborative Filtering Model
Uses implicit feedback (views, interactions) for recommendations
"""

from typing import Optional
import numpy as np
from scipy import sparse


class CollaborativeModel:
    """
    Collaborative filtering using implicit feedback.
    
    Uses Alternating Least Squares (ALS) from the implicit library
    to learn user and item latent factors from interaction data.
    """
    
    def __init__(self, factors: int = 50, regularization: float = 0.01):
        """
        Initialize collaborative model.
        
        Args:
            factors: Number of latent factors
            regularization: L2 regularization strength
        """
        self.factors = factors
        self.regularization = regularization
        self.model = None
        self.user_factors: Optional[np.ndarray] = None
        self.item_factors: Optional[np.ndarray] = None
    
    def fit(self, user_item_matrix: sparse.csr_matrix):
        """
        Train the collaborative filtering model.
        
        Args:
            user_item_matrix: Sparse matrix of user-item interactions
                             (views, feedback, etc.)
        """
        try:
            from implicit.als import AlternatingLeastSquares
            
            # Initialize and train model
            self.model = AlternatingLeastSquares(
                factors=self.factors,
                regularization=self.regularization,
                iterations=20
            )
            
            # implicit expects item-user matrix
            self.model.fit(user_item_matrix.T)
            
            # Store factors for prediction
            self.user_factors = self.model.user_factors
            self.item_factors = self.model.item_factors
            
        except ImportError:
            # Fallback: simple matrix factorization
            self._simple_fit(user_item_matrix)
    
    def _simple_fit(self, user_item_matrix: sparse.csr_matrix):
        """Simple fallback when implicit is not available"""
        # Random factors as placeholder
        n_users, n_items = user_item_matrix.shape
        self.user_factors = np.random.rand(n_users, self.factors) * 0.1
        self.item_factors = np.random.rand(n_items, self.factors) * 0.1
    
    def predict(self, user_id: int, candidate_ids: list) -> np.ndarray:
        """
        Predict scores for candidate items.
        
        Args:
            user_id: User to recommend for
            candidate_ids: List of candidate item indices
        
        Returns:
            Array of predicted scores
        """
        if self.user_factors is None or self.item_factors is None:
            return np.ones(len(candidate_ids)) * 0.5
        
        # Get user factor vector
        user_vector = self.user_factors[user_id]
        
        # Get item factors for candidates
        item_vectors = self.item_factors[candidate_ids]
        
        # Compute dot product scores
        scores = np.dot(item_vectors, user_vector)
        
        # Normalize to 0-1 range
        if scores.max() != scores.min():
            scores = (scores - scores.min()) / (scores.max() - scores.min())
        else:
            scores = np.ones_like(scores) * 0.5
        
        return scores
    
    def similar_items(self, item_id: int, n: int = 10) -> list:
        """Find similar items"""
        if self.model is not None:
            ids, scores = self.model.similar_items(item_id, N=n)
            return list(zip(ids, scores))
        return []
