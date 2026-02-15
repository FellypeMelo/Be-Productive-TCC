"""
Quality Score Calculation (RN002)
Measures content quality based on engagement and feedback
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ContentMetrics:
    """Metrics for a piece of content"""
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    total_views: int = 0
    complete_views: int = 0
    report_count: int = 0
    author_reputation: float = 0.5


def calculate_quality_score(metrics: ContentMetrics) -> float:
    """
    Calculate quality score for content (RN002).
    
    Weighted formula:
    - 40% positive feedback ratio
    - 30% complete engagement (full read/watch)
    - 20% author reputation
    - 10% absence of reports
    
    Returns:
        float: Quality score between 0 and 1
    """
    # Feedback score (40%)
    total_feedback = metrics.positive_count + metrics.neutral_count + metrics.negative_count
    if total_feedback > 0:
        feedback_score = metrics.positive_count / total_feedback
    else:
        feedback_score = 0.5  # Default for no feedback
    
    # Engagement score (30%)
    if metrics.total_views > 0:
        engagement_score = metrics.complete_views / metrics.total_views
    else:
        engagement_score = 0.5  # Default for no views
    
    # Author reputation (20%)
    author_score = max(0, min(1, metrics.author_reputation))
    
    # Report penalty (10%)
    # Each report reduces 10% of this component
    report_penalty = 1 - min(1, metrics.report_count * 0.1)
    
    # Weighted combination
    quality_score = (
        0.40 * feedback_score +
        0.30 * engagement_score +
        0.20 * author_score +
        0.10 * report_penalty
    )
    
    return max(0, min(1, quality_score))


def calculate_author_reputation(
    total_content: int,
    avg_quality_score: float,
    total_reports: int,
    account_age_days: int
) -> float:
    """
    Calculate author reputation score.
    
    Factors:
    - Average quality of their content
    - Total reports received
    - Account age (trust builds over time)
    """
    # Base from content quality
    base_score = avg_quality_score
    
    # Report penalty
    if total_content > 0:
        report_ratio = total_reports / total_content
        report_penalty = max(0, 1 - report_ratio * 2)
    else:
        report_penalty = 1.0
    
    # Age bonus (max 10% bonus after 365 days)
    age_bonus = min(0.1, account_age_days / 3650)
    
    reputation = base_score * report_penalty + age_bonus
    
    return max(0, min(1, reputation))
