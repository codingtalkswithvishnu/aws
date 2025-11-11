"""
Strands Framework Demo - Shared Models
Common data models and utilities used across agents
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class Priority(Enum):
    """Priority levels for customer issues"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CustomerTier(Enum):
    """Customer tier levels"""
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class IssueCategory(Enum):
    """Issue categories for classification"""
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    PRODUCT = "product"
    GENERAL = "general"

class Sentiment(Enum):
    """Sentiment analysis results"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

@dataclass
class CustomerProfile:
    """Customer profile data model"""
    customer_id: str
    name: str
    tier: CustomerTier
    status: str
    created_date: str
    email: Optional[str] = None
    phone: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'tier': self.tier.value,
            'status': self.status,
            'created_date': self.created_date,
            'email': self.email,
            'phone': self.phone,
            'preferences': self.preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomerProfile':
        """Create instance from dictionary"""
        return cls(
            customer_id=data['customer_id'],
            name=data['name'],
            tier=CustomerTier(data['tier']),
            status=data['status'],
            created_date=data['created_date'],
            email=data.get('email'),
            phone=data.get('phone'),
            preferences=data.get('preferences', {})
        )

@dataclass
class IssueClassification:
    """Issue classification result"""
    primary_category: IssueCategory
    subcategory: str
    confidence: float
    all_scores: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'primary_category': self.primary_category.value,
            'subcategory': self.subcategory,
            'confidence': self.confidence,
            'all_scores': self.all_scores
        }

@dataclass
class PriorityAssessment:
    """Priority assessment result"""
    level: Priority
    score: int
    factors: List[str]
    sla_target: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': self.level.value,
            'score': self.score,
            'factors': self.factors,
            'sla_target': self.sla_target
        }

@dataclass
class SentimentAnalysis:
    """Sentiment analysis result"""
    sentiment: Sentiment
    confidence: float
    word_counts: Dict[str, int]
    urgency_level: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sentiment': self.sentiment.value,
            'confidence': self.confidence,
            'word_counts': self.word_counts,
            'urgency_level': self.urgency_level
        }

@dataclass
class SolutionRecommendation:
    """Solution recommendation"""
    category: str
    subcategory: str
    immediate_actions: List[str]
    resolution_steps: List[str]
    escalation_criteria: str
    estimated_resolution_time: str
    required_permissions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'subcategory': self.subcategory,
            'immediate_actions': self.immediate_actions,
            'resolution_steps': self.resolution_steps,
            'escalation_criteria': self.escalation_criteria,
            'estimated_resolution_time': self.estimated_resolution_time,
            'required_permissions': self.required_permissions
        }

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    issue_classification: IssueClassification
    priority: PriorityAssessment
    recommended_solution: SolutionRecommendation
    sentiment: SentimentAnalysis
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'issue_classification': self.issue_classification.to_dict(),
            'priority': self.priority.to_dict(),
            'recommended_solution': self.recommended_solution.to_dict(),
            'sentiment': self.sentiment.to_dict(),
            'confidence_score': self.confidence_score
        }

@dataclass
class CustomerResponse:
    """Customer response data"""
    response_text: str
    category: str
    priority_level: str
    sla_commitment: str
    personalization_applied: bool
    sentiment_adjusted: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'response_text': self.response_text,
            'category': self.category,
            'priority_level': self.priority_level,
            'sla_commitment': self.sla_commitment,
            'personalization_applied': self.personalization_applied,
            'sentiment_adjusted': self.sentiment_adjusted
        }

@dataclass
class WorkflowContext:
    """Workflow execution context"""
    workflow_id: str
    customer_id: str
    issue_description: str
    channel: str
    timestamp: datetime
    priority_override: Optional[Priority] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'customer_id': self.customer_id,
            'issue_description': self.issue_description,
            'channel': self.channel,
            'timestamp': self.timestamp.isoformat(),
            'priority_override': self.priority_override.value if self.priority_override else None,
            'metadata': self.metadata
        }

@dataclass
class StepResult:
    """Individual step execution result"""
    step_name: str
    agent_name: str
    status: str  # completed, failed, skipped
    execution_time: float
    output: Dict[str, Any]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_name': self.step_name,
            'agent_name': self.agent_name,
            'status': self.status,
            'execution_time': self.execution_time,
            'output': self.output,
            'error_message': self.error_message
        }

@dataclass
class WorkflowResult:
    """Complete workflow execution result"""
    workflow_id: str
    customer_id: str
    status: str  # completed, escalated, failed
    customer_response: CustomerResponse
    processing_summary: Dict[str, Any]
    escalation_required: bool
    step_results: List[StepResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'customer_id': self.customer_id,
            'status': self.status,
            'customer_response': self.customer_response.to_dict(),
            'processing_summary': self.processing_summary,
            'escalation_required': self.escalation_required,
            'step_results': [step.to_dict() for step in self.step_results]
        }

# Utility functions for data validation and transformation
def validate_customer_id(customer_id: str) -> bool:
    """Validate customer ID format"""
    return isinstance(customer_id, str) and len(customer_id) > 0 and customer_id.isalnum()

def validate_priority_level(priority: str) -> bool:
    """Validate priority level"""
    try:
        Priority(priority)
        return True
    except ValueError:
        return False

def validate_customer_tier(tier: str) -> bool:
    """Validate customer tier"""
    try:
        CustomerTier(tier)
        return True
    except ValueError:
        return False

def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    """Sanitize text input for security"""
    if not isinstance(text, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized.strip()

def calculate_confidence_score(classification_confidence: float, priority_factors: int) -> float:
    """Calculate overall confidence score"""
    # Combine classification confidence with priority assessment certainty
    priority_confidence = min(priority_factors / 3, 1.0)
    overall_confidence = (classification_confidence + priority_confidence) / 2
    return round(overall_confidence, 2)

def determine_sla_target(priority: Priority, tier: CustomerTier) -> str:
    """Determine SLA target based on priority and customer tier"""
    sla_matrix = {
        Priority.CRITICAL: {
            CustomerTier.ENTERPRISE: '1 hour',
            CustomerTier.PREMIUM: '2 hours',
            CustomerTier.STANDARD: '4 hours'
        },
        Priority.HIGH: {
            CustomerTier.ENTERPRISE: '4 hours',
            CustomerTier.PREMIUM: '8 hours',
            CustomerTier.STANDARD: '24 hours'
        },
        Priority.MEDIUM: {
            CustomerTier.ENTERPRISE: '8 hours',
            CustomerTier.PREMIUM: '24 hours',
            CustomerTier.STANDARD: '48 hours'
        },
        Priority.LOW: {
            CustomerTier.ENTERPRISE: '24 hours',
            CustomerTier.PREMIUM: '48 hours',
            CustomerTier.STANDARD: '72 hours'
        }
    }
    
    return sla_matrix.get(priority, {}).get(tier, '72 hours')