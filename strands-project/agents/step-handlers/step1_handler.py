"""
Strands Framework Demo - Step 1 Handler (Data Collector)
Handles data collection phase of the customer service workflow
"""

import os
import boto3
from typing import Dict, Any, List
from strands.agent import Agent, tool

class DataCollectorAgent(Agent):
    """
    Step 1 Handler: Data Collection Agent
    Responsible for gathering customer information from multiple sources
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize AWS services
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.s3 = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for data collection step
        """
        customer_id = context.get('customer_id')
        
        # Collect data from multiple sources
        customer_profile = await self.get_customer_profile(customer_id)
        interaction_history = await self.get_interaction_history(customer_id)
        preferences = await self.get_customer_preferences(customer_id)
        
        return {
            'step': 'data_collection',
            'customer_id': customer_id,
            'data': {
                'profile': customer_profile,
                'history': interaction_history,
                'preferences': preferences
            },
            'status': 'completed'
        }
    
    @tool
    async def get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive customer profile from DynamoDB
        """
        try:
            table = self.dynamodb.Table('customer-profiles')
            response = table.get_item(Key={'customer_id': customer_id})
            
            if 'Item' in response:
                return dict(response['Item'])
            else:
                # Return default profile structure
                return {
                    'customer_id': customer_id,
                    'name': 'Unknown Customer',
                    'tier': 'standard',
                    'status': 'active',
                    'created_date': '2024-01-01'
                }
        except Exception as e:
            return {'error': f'Profile retrieval failed: {str(e)}'}
    
    @tool
    async def get_interaction_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve customer interaction history from S3
        """
        try:
            bucket = os.getenv('AGENT_S3_BUCKET', 'customer-service-documents')
            
            # List objects with customer_id prefix
            response = self.s3.list_objects_v2(
                Bucket=bucket,
                Prefix=f'interactions/{customer_id}/'
            )
            
            interactions = []
            for obj in response.get('Contents', [])[:5]:  # Get last 5 interactions
                try:
                    content = self.s3.get_object(Bucket=bucket, Key=obj['Key'])
                    interaction_data = content['Body'].read().decode('utf-8')
                    interactions.append({
                        'date': obj['LastModified'].isoformat(),
                        'data': interaction_data[:200] + '...'  # Truncate for demo
                    })
                except Exception:
                    continue
            
            return interactions
        except Exception as e:
            return [{'error': f'History retrieval failed: {str(e)}'}]
    
    @tool
    async def get_customer_preferences(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer preferences from DynamoDB
        """
        try:
            table = self.dynamodb.Table('user-preferences')
            response = table.get_item(Key={'user_id': customer_id})
            
            if 'Item' in response:
                return dict(response['Item'])
            else:
                # Return default preferences
                return {
                    'communication_channel': 'email',
                    'language': 'en',
                    'timezone': 'UTC',
                    'notification_frequency': 'normal'
                }
        except Exception as e:
            return {'error': f'Preferences retrieval failed: {str(e)}'}
    
    @tool
    def validate_customer_data(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate collected customer data for completeness and accuracy
        """
        validation_results = {
            'is_valid': True,
            'missing_fields': [],
            'warnings': []
        }
        
        required_fields = ['customer_id', 'name', 'tier', 'status']
        profile = customer_data.get('profile', {})
        
        for field in required_fields:
            if field not in profile or not profile[field]:
                validation_results['missing_fields'].append(field)
                validation_results['is_valid'] = False
        
        # Check for data quality issues
        if profile.get('tier') not in ['standard', 'premium', 'enterprise']:
            validation_results['warnings'].append('Invalid customer tier')
        
        if profile.get('status') not in ['active', 'inactive', 'suspended']:
            validation_results['warnings'].append('Invalid customer status')
        
        return validation_results

# Agent instance for Strands runtime
agent = DataCollectorAgent()