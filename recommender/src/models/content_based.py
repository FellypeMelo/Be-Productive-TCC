"""
Content-Based Filtering Model
Uses topic/tag similarity for recommendations
"""

from typing import Optional
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedModel:
    """
    Content-based recommendation using topic similarity.
    
    Computes similarity between user topic preferences and
    content topic associations using TF-IDF weighted cosine similarity.
    """
    
    def __init__(self):
        self.user_topic_matrix: Optional[sparse.csr_matrix] = None
        self.content_topic_matrix: Optional[sparse.csr_matrix] = None
        self._user_profiles: Optional[np.ndarray] = None
    
    def fit(
        self,
        user_topic_matrix: sparse.csr_matrix,
        content_topic_matrix: sparse.csr_matrix
    ):
        """
        Fit the content-based model.
        
        Args:
            user_topic_matrix: Sparse matrix (n_users, n_topics)
            content_topic_matrix: Sparse matrix (n_content, n_topics)
        """
        self.user_topic_matrix = user_topic_matrix
        self.content_topic_matrix = content_topic_matrix
        
        # Pre-compute normalized user profiles
        self._user_profiles = self._normalize_matrix(user_topic_matrix.toarray())
    
    def predict(self, user_id: int, candidate_ids: list) -> np.ndarray:
        """
        Predict scores for candidate content.
        
        Args:
            user_id: User to recommend for
            candidate_ids: List of candidate content indices
        
        Returns:
            Array of similarity scores
        """
        if self._user_profiles is None:
            return np.ones(len(candidate_ids)) * 0.5
        
        # Get user profile
        user_profile = self._user_profiles[user_id].reshape(1, -1)
        
        # Get content profiles for candidates
        content_profiles = self.content_topic_matrix[candidate_ids].toarray()
        content_profiles = self._normalize_matrix(content_profiles)
        
        # Compute cosine similarity
        similarities = cosine_similarity(user_profile, content_profiles).flatten()
        
        return similarities
    
    def _normalize_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """L2 normalize rows of a matrix"""
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return matrix / norms
