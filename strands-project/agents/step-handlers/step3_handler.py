"""
Strands Framework Demo - Step 3 Handler (Reporter)
Handles reporting and response generation phase of the customer service workflow
"""

import os
import json
import boto3
from datetime import datetime
from typing import Dict, Any, List
from strands.agent import Agent, tool

class ReporterAgent(Agent):
    """
    Step 3 Handler: Reporter Agent
    Responsible for generating reports and customer responses
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize AWS services
        self.s3 = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for reporting step
        """
        analysis = context.get('analysis', {})
        customer_data = context.get('data', {})
        customer_id = context.get('customer_id')
        
        # Generate customer response
        customer_response = await self.generate_customer_response(analysis, customer_data)
        
        # Create internal report
        internal_report = await self.create_internal_report(analysis, customer_data, customer_response)
        
        # Store results
        storage_results = await self.store_results(customer_id, internal_report, customer_response)
        
        # Send notifications if needed
        notifications = await self.send_notifications(analysis, customer_id)
        
        return {
            'step': 'reporting',
            'customer_id': customer_id,
            'outputs': {
                'customer_response': customer_response,
                'internal_report': internal_report,
                'storage_results': storage_results,
                'notifications': notifications
            },
            'status': 'completed'
        }
    
    @tool
    async def generate_customer_response(self, analysis: Dict[str, Any], customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized customer response based on analysis
        """
        issue_classification = analysis.get('issue_classification', {})
        priority = analysis.get('priority', {})
        solution = analysis.get('recommended_solution', {})
        sentiment = analysis.get('sentiment', {})
        
        category = issue_classification.get('primary_category', 'general')
        priority_level = priority.get('level', 'medium')
        customer_tier = customer_data.get('profile', {}).get('tier', 'standard')
        
        # Base response templates
        response_templates = {
            'billing': {
                'greeting': "Thank you for contacting us regarding your billing inquiry.",
                'acknowledgment': "I've reviewed your account and understand your concern about the billing issue.",
                'action': "I'm working to resolve this matter promptly and will ensure any necessary adjustments are made.",
                'next_steps': "You can expect a resolution within {sla_time}, and I'll keep you updated on our progress."
            },
            'technical': {
                'greeting': "Thank you for reporting this technical issue.",
                'acknowledgment': "I understand how frustrating technical problems can be, and I'm here to help.",
                'action': "I've initiated our troubleshooting process and am working with our technical team to identify the root cause.",
                'next_steps': "I'll provide you with a solution or workaround within {sla_time}."
            },
            'account': {
                'greeting': "Thank you for contacting us about your account.",
                'acknowledgment': "I've reviewed your account status and understand your concern.",
                'action': "I'm taking immediate steps to address your account-related issue.",
                'next_steps': "Your account issue will be resolved within {sla_time}."
            },
            'product': {
                'greeting': "Thank you for your product inquiry.",
                'acknowledgment': "I understand you need assistance with our product features.",
                'action': "I'm gathering the relevant information and resources to help you achieve your goals.",
                'next_steps': "I'll provide you with detailed guidance within {sla_time}."
            }
        }
        
        template = response_templates.get(category, response_templates['product'])
        sla_time = priority.get('sla_target', '24 hours')
        
        # Customize based on sentiment
        if sentiment.get('sentiment') == 'negative' and sentiment.get('confidence', 0) > 0.7:
            template['acknowledgment'] = f"I sincerely apologize for the inconvenience you've experienced. {template['acknowledgment']}"
        
        # Customize based on customer tier
        if customer_tier in ['premium', 'enterprise']:
            template['greeting'] = f"Dear Valued {customer_tier.title()} Customer, {template['greeting']}"
            template['next_steps'] = f"As a {customer_tier} customer, {template['next_steps'].lower()}"
        
        # Format the complete response
        response_text = f"{template['greeting']} {template['acknowledgment']} {template['action']} {template['next_steps'].format(sla_time=sla_time)}"
        
        return {
            'response_text': response_text,
            'category': category,
            'priority_level': priority_level,
            'sla_commitment': sla_time,
            'personalization_applied': True,
            'sentiment_adjusted': sentiment.get('sentiment') == 'negative'
        }
    
    @tool
    async def create_internal_report(self, analysis: Dict[str, Any], customer_data: Dict[str, Any], customer_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive internal report for tracking and analytics
        """
        report = {
            'report_id': f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.utcnow().isoformat(),
            'customer_info': {
                'customer_id': customer_data.get('profile', {}).get('customer_id'),
                'tier': customer_data.get('profile', {}).get('tier'),
                'status': customer_data.get('profile', {}).get('status')
            },
            'issue_analysis': {
                'category': analysis.get('issue_classification', {}).get('primary_category'),
                'subcategory': analysis.get('issue_classification', {}).get('subcategory'),
                'priority': analysis.get('priority', {}).get('level'),
                'confidence_score': analysis.get('confidence_score'),
                'sentiment': analysis.get('sentiment', {}).get('sentiment')
            },
            'resolution_info': {
                'sla_target': analysis.get('priority', {}).get('sla_target'),
                'estimated_resolution': analysis.get('recommended_solution', {}).get('estimated_resolution_time'),
                'required_permissions': analysis.get('recommended_solution', {}).get('required_permissions', []),
                'escalation_criteria': analysis.get('recommended_solution', {}).get('solution_template', {}).get('escalation_criteria')
            },
            'response_details': {
                'response_category': customer_response.get('category'),
                'personalization_applied': customer_response.get('personalization_applied'),
                'sentiment_adjusted': customer_response.get('sentiment_adjusted')
            },
            'metrics': {
                'processing_time': self.calculate_processing_time(),
                'automation_level': 'full',
                'human_intervention_required': self.requires_human_intervention(analysis)
            }
        }
        
        return report
    
    @tool
    async def store_results(self, customer_id: str, report: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store results in S3 and DynamoDB for future reference
        """
        storage_results = {
            's3_storage': {'success': False, 'location': None},
            'dynamodb_storage': {'success': False, 'table': None},
            'errors': []
        }
        
        try:
            # Store detailed report in S3
            bucket = os.getenv('AGENT_S3_BUCKET', 'customer-service-documents')
            report_key = f"reports/{customer_id}/{report['report_id']}.json"
            
            self.s3.put_object(
                Bucket=bucket,
                Key=report_key,
                Body=json.dumps(report, indent=2),
                ContentType='application/json'
            )
            
            storage_results['s3_storage'] = {
                'success': True,
                'location': f's3://{bucket}/{report_key}'
            }
            
        except Exception as e:
            storage_results['errors'].append(f'S3 storage failed: {str(e)}')
        
        try:
            # Store summary in DynamoDB for quick access
            table = self.dynamodb.Table('interaction-summaries')
            
            summary_item = {
                'customer_id': customer_id,
                'report_id': report['report_id'],
                'timestamp': report['timestamp'],
                'category': report['issue_analysis']['category'],
                'priority': report['issue_analysis']['priority'],
                'status': 'completed',
                'sla_target': report['resolution_info']['sla_target'],
                's3_location': storage_results['s3_storage'].get('location')
            }
            
            table.put_item(Item=summary_item)
            
            storage_results['dynamodb_storage'] = {
                'success': True,
                'table': 'interaction-summaries'
            }
            
        except Exception as e:
            storage_results['errors'].append(f'DynamoDB storage failed: {str(e)}')
        
        return storage_results
    
    @tool
    async def send_notifications(self, analysis: Dict[str, Any], customer_id: str) -> Dict[str, Any]:
        """
        Send notifications based on analysis results
        """
        notifications = {
            'sent': [],
            'failed': [],
            'skipped': []
        }
        
        priority_level = analysis.get('priority', {}).get('level', 'medium')
        category = analysis.get('issue_classification', {}).get('primary_category', 'general')
        
        # High priority notifications
        if priority_level in ['critical', 'high']:
            try:
                # Simulate sending notification to management
                notification_result = await self.send_management_notification(customer_id, priority_level, category)
                notifications['sent'].append({
                    'type': 'management_alert',
                    'recipient': 'support-management@company.com',
                    'result': notification_result
                })
            except Exception as e:
                notifications['failed'].append({
                    'type': 'management_alert',
                    'error': str(e)
                })
        
        # Technical issue notifications
        if category == 'technical':
            try:
                # Simulate sending notification to technical team
                notification_result = await self.send_technical_notification(customer_id, analysis)
                notifications['sent'].append({
                    'type': 'technical_team_alert',
                    'recipient': 'technical-team@company.com',
                    'result': notification_result
                })
            except Exception as e:
                notifications['failed'].append({
                    'type': 'technical_team_alert',
                    'error': str(e)
                })
        
        # Customer confirmation notification
        try:
            confirmation_result = await self.send_customer_confirmation(customer_id)
            notifications['sent'].append({
                'type': 'customer_confirmation',
                'recipient': f'customer_{customer_id}',
                'result': confirmation_result
            })
        except Exception as e:
            notifications['failed'].append({
                'type': 'customer_confirmation',
                'error': str(e)
            })
        
        return notifications
    
    async def send_management_notification(self, customer_id: str, priority: str, category: str) -> Dict[str, Any]:
        """Send notification to management for high priority issues"""
        # Simulate notification sending
        return {
            'status': 'sent',
            'message': f'High priority {category} issue for customer {customer_id}',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def send_technical_notification(self, customer_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification to technical team"""
        # Simulate notification sending
        return {
            'status': 'sent',
            'message': f'Technical issue reported by customer {customer_id}',
            'analysis_summary': analysis.get('issue_classification', {}),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def send_customer_confirmation(self, customer_id: str) -> Dict[str, Any]:
        """Send confirmation to customer"""
        # Simulate notification sending
        return {
            'status': 'sent',
            'message': 'Support request received and being processed',
            'customer_id': customer_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def calculate_processing_time(self) -> str:
        """Calculate processing time (simulated for demo)"""
        import random
        processing_seconds = random.randint(5, 30)
        return f"{processing_seconds} seconds"
    
    def requires_human_intervention(self, analysis: Dict[str, Any]) -> bool:
        """Determine if human intervention is required"""
        priority_level = analysis.get('priority', {}).get('level', 'medium')
        confidence_score = analysis.get('confidence_score', 0.0)
        
        # Require human intervention for critical issues or low confidence
        return priority_level == 'critical' or confidence_score < 0.6
    
    @tool
    def generate_summary_metrics(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary metrics for reporting dashboard"""
        return {
            'total_processing_time': report.get('metrics', {}).get('processing_time'),
            'automation_success': True,
            'confidence_score': report.get('issue_analysis', {}).get('confidence_score'),
            'priority_level': report.get('issue_analysis', {}).get('priority'),
            'category': report.get('issue_analysis', {}).get('category'),
            'human_intervention_required': report.get('metrics', {}).get('human_intervention_required'),
            'sla_compliance': 'on_track'  # Would be calculated based on actual timing
        }

# Agent instance for Strands runtime
agent = ReporterAgent()