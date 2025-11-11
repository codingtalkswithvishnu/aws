"""
Strands Framework Demo - Coordinator Agent
Main orchestrator for customer service workflows
"""

import os
import json
import boto3
import requests
from typing import Dict, List, Any
from strands.agent import Agent, tool
from strands.memory import MemoryStore
from strands.mcp import MCPClient

class CustomerServiceCoordinator(Agent):
    """
    Main coordinator agent that orchestrates the customer service workflow.
    Demonstrates multi-step workflow coordination and tool integration.
    """
    
    def __init__(self):
        super().__init__()
        self.memory_store = MemoryStore()
        
        # Initialize MCP client for filesystem operations
        self.mcp_client = MCPClient(
            "npx @modelcontextprotocol/server-filesystem /customer-files"
        )
        
        # Initialize AWS clients with proper region configuration
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.s3 = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    async def process_customer_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main workflow orchestration method.
        Coordinates between data collection, analysis, and reporting steps.
        """
        customer_id = request.get('customer_id')
        issue_description = request.get('issue_description')
        
        # Step 1: Collect customer data
        customer_data = await self.collect_customer_data(customer_id)
        
        # Step 2: Analyze the issue
        analysis = await self.analyze_customer_issue(customer_data, issue_description)
        
        # Step 3: Generate response and store results
        response = await self.generate_customer_response(analysis)
        
        # Store interaction for future reference
        await self.store_interaction_history(customer_id, request, response)
        
        return {
            'customer_id': customer_id,
            'status': 'completed',
            'response': response,
            'analysis': analysis
        }
    
    @tool
    def get_weather(self, city: str) -> str:
        """
        Get current weather for a city using external API.
        Demonstrates REST API integration with proper error handling.
        """
        try:
            response = requests.get(
                f"https://api.weather.com/v1/current",
                params={
                    "q": city, 
                    "key": os.getenv("WEATHER_API_KEY")
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()["current"]["condition"]
        except requests.RequestException as e:
            return f"Weather service unavailable: {str(e)}"
    
    @tool
    def query_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer information from database.
        Demonstrates secure database connectivity with parameterized queries.
        """
        try:
            table = self.dynamodb.Table('customer-profiles')
            response = table.get_item(Key={'customer_id': customer_id})
            
            if 'Item' in response:
                return dict(response['Item'])
            else:
                return {'error': 'Customer not found'}
        except Exception as e:
            return {'error': f'Database error: {str(e)}'}
    
    @tool
    def store_user_preference(self, user_id: str, preference: Dict[str, Any]) -> bool:
        """
        Store user preferences in DynamoDB.
        Demonstrates persistent memory storage with AWS services.
        """
        try:
            table = self.dynamodb.Table('user-preferences')
            table.put_item(Item={'user_id': user_id, **preference})
            return True
        except Exception as e:
            print(f"Error storing preference: {e}")
            return False
    
    @tool
    def store_document(self, doc_id: str, content: str) -> str:
        """
        Store document in S3 for agent reference.
        Demonstrates document storage with proper S3 integration.
        """
        try:
            bucket = os.getenv('AGENT_S3_BUCKET', 'customer-service-documents')
            self.s3.put_object(
                Bucket=bucket,
                Key=f'docs/{doc_id}.txt',
                Body=content,
                ContentType='text/plain'
            )
            return f's3://{bucket}/docs/{doc_id}.txt'
        except Exception as e:
            return f'Error storing document: {str(e)}'
    
    @tool
    def cache_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Cache temporary session data in ElastiCache.
        Demonstrates fast temporary memory with Redis integration.
        """
        try:
            import redis
            endpoint = os.getenv('ELASTICACHE_ENDPOINT')
            r = redis.Redis(host=endpoint, port=6379, decode_responses=True)
            r.setex(f'session:{session_id}', 3600, json.dumps(data))
            return True
        except Exception as e:
            print(f"Error caching session data: {e}")
            return False
    
    @tool
    def read_file_via_mcp(self, filepath: str) -> str:
        """
        Read file using MCP filesystem server.
        Demonstrates Model Context Protocol integration.
        """
        try:
            return self.mcp_client.call_tool("read_file", {"path": filepath})
        except Exception as e:
            return f"MCP error: {str(e)}"
    
    @tool
    def search_files_via_mcp(self, query: str) -> List[str]:
        """
        Search files using MCP server.
        Demonstrates advanced MCP tool usage for file operations.
        """
        try:
            return self.mcp_client.call_tool("search_files", {"query": query})
        except Exception as e:
            return [f"MCP search error: {str(e)}"]
    
    async def collect_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Step 1: Data collection with multiple sources"""
        customer_profile = self.query_customer(customer_id)
        
        # Get cached session data if available
        import redis
        try:
            endpoint = os.getenv('ELASTICACHE_ENDPOINT')
            r = redis.Redis(host=endpoint, port=6379, decode_responses=True)
            cached_data = r.get(f'session:{customer_id}')
            session_data = json.loads(cached_data) if cached_data else {}
        except:
            session_data = {}
        
        return {
            'profile': customer_profile,
            'session': session_data,
            'timestamp': self.get_current_timestamp()
        }
    
    async def analyze_customer_issue(self, customer_data: Dict[str, Any], issue: str) -> Dict[str, Any]:
        """Step 2: Issue analysis with AI reasoning"""
        # This would typically involve calling Bedrock or other AI services
        # For demo purposes, we'll simulate analysis
        
        analysis = {
            'issue_type': self.classify_issue(issue),
            'priority': self.determine_priority(customer_data, issue),
            'suggested_actions': self.suggest_actions(issue),
            'confidence': 0.85
        }
        
        return analysis
    
    async def generate_customer_response(self, analysis: Dict[str, Any]) -> str:
        """Step 3: Response generation based on analysis"""
        issue_type = analysis.get('issue_type', 'general')
        priority = analysis.get('priority', 'medium')
        
        response_templates = {
            'billing': "Thank you for contacting us about your billing inquiry. I've reviewed your account and can help resolve this issue.",
            'technical': "I understand you're experiencing technical difficulties. Let me walk you through the solution.",
            'general': "Thank you for reaching out. I'm here to help with your inquiry."
        }
        
        base_response = response_templates.get(issue_type, response_templates['general'])
        
        if priority == 'high':
            base_response = f"URGENT: {base_response} I'm prioritizing your request for immediate resolution."
        
        return base_response
    
    async def store_interaction_history(self, customer_id: str, request: Dict[str, Any], response: Dict[str, Any]) -> bool:
        """Store interaction for future reference and learning"""
        interaction_data = {
            'customer_id': customer_id,
            'timestamp': self.get_current_timestamp(),
            'request': request,
            'response': response
        }
        
        # Store in S3 for long-term retention
        doc_id = f"interaction_{customer_id}_{self.get_current_timestamp()}"
        self.store_document(doc_id, json.dumps(interaction_data, indent=2))
        
        return True
    
    def classify_issue(self, issue: str) -> str:
        """Simple issue classification logic"""
        issue_lower = issue.lower()
        if any(word in issue_lower for word in ['bill', 'charge', 'payment', 'invoice']):
            return 'billing'
        elif any(word in issue_lower for word in ['error', 'bug', 'not working', 'broken']):
            return 'technical'
        else:
            return 'general'
    
    def determine_priority(self, customer_data: Dict[str, Any], issue: str) -> str:
        """Determine issue priority based on customer data and issue content"""
        profile = customer_data.get('profile', {})
        customer_tier = profile.get('tier', 'standard')
        
        if customer_tier == 'premium' or 'urgent' in issue.lower():
            return 'high'
        elif 'asap' in issue.lower() or 'immediately' in issue.lower():
            return 'medium'
        else:
            return 'low'
    
    def suggest_actions(self, issue: str) -> List[str]:
        """Suggest actions based on issue analysis"""
        actions = ['Log issue in system', 'Send acknowledgment to customer']
        
        if 'billing' in issue.lower():
            actions.append('Review billing history')
            actions.append('Check payment status')
        elif 'technical' in issue.lower():
            actions.append('Run diagnostic checks')
            actions.append('Escalate to technical team if needed')
        
        return actions
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Agent instance for Strands runtime
agent = CustomerServiceCoordinator()