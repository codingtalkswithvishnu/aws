"""
Strands Framework Demo - Step 2 Handler (Analyzer)
Handles analysis phase of the customer service workflow
"""

import os
import json
from typing import Dict, Any, List
from strands.agent import Agent, tool

class AnalyzerAgent(Agent):
    """
    Step 2 Handler: Analysis Agent
    Responsible for analyzing customer issues and determining appropriate solutions
    """
    
    def __init__(self):
        super().__init__()
        
        # Load analysis rules and patterns
        self.issue_patterns = self.load_issue_patterns()
        self.solution_templates = self.load_solution_templates()
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for analysis step
        """
        customer_data = context.get('data', {})
        issue_description = context.get('issue_description', '')
        
        # Perform comprehensive analysis
        issue_classification = await self.classify_issue(issue_description)
        priority_assessment = await self.assess_priority(customer_data, issue_description)
        solution_recommendation = await self.recommend_solution(issue_classification, customer_data)
        sentiment_analysis = await self.analyze_sentiment(issue_description)
        
        analysis_result = {
            'step': 'analysis',
            'customer_id': context.get('customer_id'),
            'analysis': {
                'issue_classification': issue_classification,
                'priority': priority_assessment,
                'recommended_solution': solution_recommendation,
                'sentiment': sentiment_analysis,
                'confidence_score': self.calculate_confidence(issue_classification, priority_assessment)
            },
            'status': 'completed'
        }
        
        return analysis_result
    
    @tool
    async def classify_issue(self, issue_description: str) -> Dict[str, Any]:
        """
        Classify the customer issue into predefined categories
        """
        issue_lower = issue_description.lower()
        
        # Define classification patterns
        classifications = {
            'billing': {
                'keywords': ['bill', 'charge', 'payment', 'invoice', 'refund', 'cost', 'price'],
                'confidence': 0.0
            },
            'technical': {
                'keywords': ['error', 'bug', 'not working', 'broken', 'crash', 'slow', 'issue'],
                'confidence': 0.0
            },
            'account': {
                'keywords': ['account', 'login', 'password', 'access', 'profile', 'settings'],
                'confidence': 0.0
            },
            'product': {
                'keywords': ['feature', 'product', 'service', 'functionality', 'how to', 'usage'],
                'confidence': 0.0
            },
            'general': {
                'keywords': ['help', 'support', 'question', 'inquiry', 'information'],
                'confidence': 0.0
            }
        }
        
        # Calculate confidence scores based on keyword matches
        words = issue_lower.split()
        total_words = len(words)
        
        for category, data in classifications.items():
            matches = sum(1 for word in words if any(keyword in word for keyword in data['keywords']))
            data['confidence'] = matches / total_words if total_words > 0 else 0.0
        
        # Find the category with highest confidence
        best_category = max(classifications.items(), key=lambda x: x[1]['confidence'])
        
        return {
            'primary_category': best_category[0],
            'confidence': best_category[1]['confidence'],
            'all_scores': {cat: data['confidence'] for cat, data in classifications.items()},
            'subcategory': self.determine_subcategory(best_category[0], issue_description)
        }
    
    @tool
    async def assess_priority(self, customer_data: Dict[str, Any], issue_description: str) -> Dict[str, Any]:
        """
        Assess the priority level of the customer issue
        """
        priority_score = 0
        factors = []
        
        # Customer tier factor
        profile = customer_data.get('profile', {})
        customer_tier = profile.get('tier', 'standard')
        
        if customer_tier == 'enterprise':
            priority_score += 3
            factors.append('Enterprise customer')
        elif customer_tier == 'premium':
            priority_score += 2
            factors.append('Premium customer')
        else:
            priority_score += 1
            factors.append('Standard customer')
        
        # Urgency keywords
        urgency_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'down', 'broken']
        issue_lower = issue_description.lower()
        
        urgency_matches = sum(1 for keyword in urgency_keywords if keyword in issue_lower)
        priority_score += urgency_matches * 2
        
        if urgency_matches > 0:
            factors.append(f'Urgency indicators: {urgency_matches}')
        
        # Business impact assessment
        impact_keywords = ['revenue', 'business', 'production', 'customers', 'sales', 'system']
        impact_matches = sum(1 for keyword in impact_keywords if keyword in issue_lower)
        priority_score += impact_matches
        
        if impact_matches > 0:
            factors.append(f'Business impact indicators: {impact_matches}')
        
        # Determine priority level
        if priority_score >= 6:
            priority_level = 'critical'
        elif priority_score >= 4:
            priority_level = 'high'
        elif priority_score >= 2:
            priority_level = 'medium'
        else:
            priority_level = 'low'
        
        return {
            'level': priority_level,
            'score': priority_score,
            'factors': factors,
            'sla_target': self.get_sla_target(priority_level, customer_tier)
        }
    
    @tool
    async def recommend_solution(self, classification: Dict[str, Any], customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend appropriate solution based on issue classification and customer data
        """
        category = classification.get('primary_category', 'general')
        subcategory = classification.get('subcategory', 'general')
        
        # Solution templates based on category
        solutions = {
            'billing': {
                'immediate_actions': [
                    'Review customer billing history',
                    'Check payment status and methods',
                    'Verify billing address and information'
                ],
                'resolution_steps': [
                    'Investigate billing discrepancy',
                    'Process refund if applicable',
                    'Update billing preferences'
                ],
                'escalation_criteria': 'Amount > $500 or legal implications'
            },
            'technical': {
                'immediate_actions': [
                    'Gather system information and error logs',
                    'Reproduce the issue if possible',
                    'Check system status and known issues'
                ],
                'resolution_steps': [
                    'Apply standard troubleshooting steps',
                    'Escalate to technical team if needed',
                    'Provide workaround if available'
                ],
                'escalation_criteria': 'System-wide impact or security concerns'
            },
            'account': {
                'immediate_actions': [
                    'Verify customer identity',
                    'Check account status and permissions',
                    'Review recent account activity'
                ],
                'resolution_steps': [
                    'Reset credentials if needed',
                    'Update account settings',
                    'Provide security recommendations'
                ],
                'escalation_criteria': 'Suspected security breach'
            },
            'product': {
                'immediate_actions': [
                    'Understand specific use case',
                    'Check product documentation',
                    'Identify feature limitations'
                ],
                'resolution_steps': [
                    'Provide step-by-step guidance',
                    'Share relevant documentation',
                    'Suggest alternative approaches'
                ],
                'escalation_criteria': 'Feature request or product limitation'
            }
        }
        
        solution = solutions.get(category, solutions['product'])  # Default to product
        
        # Customize based on customer tier
        profile = customer_data.get('profile', {})
        customer_tier = profile.get('tier', 'standard')
        
        if customer_tier in ['premium', 'enterprise']:
            solution['immediate_actions'].insert(0, 'Assign dedicated support representative')
            solution['additional_benefits'] = ['Priority handling', 'Direct escalation path']
        
        return {
            'category': category,
            'subcategory': subcategory,
            'solution_template': solution,
            'estimated_resolution_time': self.estimate_resolution_time(category, customer_tier),
            'required_permissions': self.get_required_permissions(category)
        }
    
    @tool
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the customer message
        Simple rule-based sentiment analysis for demo purposes
        """
        positive_words = ['good', 'great', 'excellent', 'happy', 'satisfied', 'love', 'perfect', 'amazing']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'frustrated', 'disappointed', 'broken']
        neutral_words = ['okay', 'fine', 'normal', 'standard', 'regular']
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if any(pos in word for pos in positive_words))
        negative_count = sum(1 for word in words if any(neg in word for neg in negative_words))
        neutral_count = sum(1 for word in words if any(neu in word for neu in neutral_words))
        
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            sentiment = 'neutral'
            confidence = 0.5
        else:
            if negative_count > positive_count:
                sentiment = 'negative'
                confidence = negative_count / total_sentiment_words
            elif positive_count > negative_count:
                sentiment = 'positive'
                confidence = positive_count / total_sentiment_words
            else:
                sentiment = 'neutral'
                confidence = neutral_count / total_sentiment_words if neutral_count > 0 else 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': min(confidence, 1.0),
            'word_counts': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            },
            'urgency_level': 'high' if negative_count > 2 else 'normal'
        }
    
    def determine_subcategory(self, category: str, issue_description: str) -> str:
        """Determine subcategory based on main category and description"""
        subcategories = {
            'billing': ['invoice', 'payment', 'refund', 'pricing'],
            'technical': ['login', 'performance', 'error', 'integration'],
            'account': ['access', 'settings', 'profile', 'security'],
            'product': ['features', 'usage', 'documentation', 'training']
        }
        
        issue_lower = issue_description.lower()
        category_subs = subcategories.get(category, ['general'])
        
        for sub in category_subs:
            if sub in issue_lower:
                return sub
        
        return 'general'
    
    def calculate_confidence(self, classification: Dict[str, Any], priority: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the analysis"""
        class_confidence = classification.get('confidence', 0.0)
        priority_factors = len(priority.get('factors', []))
        
        # Combine classification confidence with priority assessment certainty
        confidence = (class_confidence + min(priority_factors / 3, 1.0)) / 2
        return round(confidence, 2)
    
    def get_sla_target(self, priority_level: str, customer_tier: str) -> str:
        """Get SLA target based on priority and customer tier"""
        sla_matrix = {
            'critical': {'enterprise': '1 hour', 'premium': '2 hours', 'standard': '4 hours'},
            'high': {'enterprise': '4 hours', 'premium': '8 hours', 'standard': '24 hours'},
            'medium': {'enterprise': '8 hours', 'premium': '24 hours', 'standard': '48 hours'},
            'low': {'enterprise': '24 hours', 'premium': '48 hours', 'standard': '72 hours'}
        }
        
        return sla_matrix.get(priority_level, {}).get(customer_tier, '72 hours')
    
    def estimate_resolution_time(self, category: str, customer_tier: str) -> str:
        """Estimate resolution time based on issue category and customer tier"""
        base_times = {
            'billing': '2-4 hours',
            'technical': '4-8 hours',
            'account': '1-2 hours',
            'product': '2-6 hours',
            'general': '2-4 hours'
        }
        
        base_time = base_times.get(category, '2-4 hours')
        
        if customer_tier in ['premium', 'enterprise']:
            return f"{base_time} (Priority handling)"
        
        return base_time
    
    def get_required_permissions(self, category: str) -> List[str]:
        """Get required permissions for handling specific issue categories"""
        permissions = {
            'billing': ['billing_read', 'billing_write', 'refund_process'],
            'technical': ['system_access', 'log_access', 'escalation_create'],
            'account': ['account_read', 'account_write', 'security_reset'],
            'product': ['documentation_access', 'feature_info'],
            'general': ['basic_support']
        }
        
        return permissions.get(category, ['basic_support'])
    
    def load_issue_patterns(self) -> Dict[str, Any]:
        """Load issue classification patterns (placeholder for ML models)"""
        return {
            'patterns_loaded': True,
            'model_version': '1.0',
            'last_updated': '2024-01-01'
        }
    
    def load_solution_templates(self) -> Dict[str, Any]:
        """Load solution templates (placeholder for knowledge base)"""
        return {
            'templates_loaded': True,
            'template_count': 150,
            'last_updated': '2024-01-01'
        }

# Agent instance for Strands runtime
agent = AnalyzerAgent()