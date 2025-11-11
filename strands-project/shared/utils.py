"""
Strands Framework Demo - Shared Utilities
Common utility functions used across agents
"""

import os
import json
import logging
import boto3
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSServiceManager:
    """Centralized AWS service management"""
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self._dynamodb = None
        self._s3 = None
        self._redis = None
    
    @property
    def dynamodb(self):
        """Lazy-loaded DynamoDB resource"""
        if self._dynamodb is None:
            try:
                self._dynamodb = boto3.resource('dynamodb', region_name=self.region)
            except NoCredentialsError:
                logger.error("AWS credentials not configured")
                raise
        return self._dynamodb
    
    @property
    def s3(self):
        """Lazy-loaded S3 client"""
        if self._s3 is None:
            try:
                self._s3 = boto3.client('s3', region_name=self.region)
            except NoCredentialsError:
                logger.error("AWS credentials not configured")
                raise
        return self._s3
    
    @property
    def redis_client(self):
        """Lazy-loaded Redis client"""
        if self._redis is None:
            endpoint = os.getenv('ELASTICACHE_ENDPOINT')
            if endpoint:
                try:
                    self._redis = redis.Redis(
                        host=endpoint,
                        port=6379,
                        decode_responses=True,
                        socket_timeout=5,
                        socket_connect_timeout=5
                    )
                    # Test connection
                    self._redis.ping()
                except redis.ConnectionError:
                    logger.warning("Redis connection failed, caching disabled")
                    self._redis = None
        return self._redis

# Global AWS service manager instance
aws_manager = AWSServiceManager()

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()

def get_timestamp_hours_ago(hours: int) -> str:
    """Get timestamp from hours ago"""
    past_time = datetime.utcnow() - timedelta(hours=hours)
    return past_time.isoformat()

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {json_string[:100]}...")
        return default

def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """Safely serialize data to JSON with fallback"""
    try:
        return json.dumps(data, indent=2, default=str)
    except (TypeError, ValueError):
        logger.warning(f"Failed to serialize data: {type(data)}")
        return default

def cache_get(key: str, default: Any = None) -> Any:
    """Get value from Redis cache"""
    try:
        if aws_manager.redis_client:
            value = aws_manager.redis_client.get(key)
            if value:
                return safe_json_loads(value, default)
    except Exception as e:
        logger.warning(f"Cache get failed for key {key}: {e}")
    return default

def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set value in Redis cache with TTL"""
    try:
        if aws_manager.redis_client:
            json_value = safe_json_dumps(value)
            aws_manager.redis_client.setex(key, ttl, json_value)
            return True
    except Exception as e:
        logger.warning(f"Cache set failed for key {key}: {e}")
    return False

def cache_delete(key: str) -> bool:
    """Delete key from Redis cache"""
    try:
        if aws_manager.redis_client:
            aws_manager.redis_client.delete(key)
            return True
    except Exception as e:
        logger.warning(f"Cache delete failed for key {key}: {e}")
    return False

def dynamodb_get_item(table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get item from DynamoDB table"""
    try:
        table = aws_manager.dynamodb.Table(table_name)
        response = table.get_item(Key=key)
        return dict(response['Item']) if 'Item' in response else None
    except ClientError as e:
        logger.error(f"DynamoDB get_item failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in DynamoDB get_item: {e}")
        return None

def dynamodb_put_item(table_name: str, item: Dict[str, Any]) -> bool:
    """Put item to DynamoDB table"""
    try:
        table = aws_manager.dynamodb.Table(table_name)
        table.put_item(Item=item)
        return True
    except ClientError as e:
        logger.error(f"DynamoDB put_item failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in DynamoDB put_item: {e}")
        return False

def dynamodb_query_items(table_name: str, key_condition: str, **kwargs) -> List[Dict[str, Any]]:
    """Query items from DynamoDB table"""
    try:
        table = aws_manager.dynamodb.Table(table_name)
        response = table.query(KeyConditionExpression=key_condition, **kwargs)
        return [dict(item) for item in response.get('Items', [])]
    except ClientError as e:
        logger.error(f"DynamoDB query failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in DynamoDB query: {e}")
        return []

def s3_put_object(bucket: str, key: str, body: str, content_type: str = 'text/plain') -> bool:
    """Put object to S3 bucket"""
    try:
        aws_manager.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=content_type
        )
        return True
    except ClientError as e:
        logger.error(f"S3 put_object failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in S3 put_object: {e}")
        return False

def s3_get_object(bucket: str, key: str) -> Optional[str]:
    """Get object from S3 bucket"""
    try:
        response = aws_manager.s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read().decode('utf-8')
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.info(f"S3 object not found: {key}")
        else:
            logger.error(f"S3 get_object failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in S3 get_object: {e}")
        return None

def s3_list_objects(bucket: str, prefix: str = '', max_keys: int = 1000) -> List[Dict[str, Any]]:
    """List objects in S3 bucket"""
    try:
        response = aws_manager.s3.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        return response.get('Contents', [])
    except ClientError as e:
        logger.error(f"S3 list_objects failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in S3 list_objects: {e}")
        return []

def validate_environment_variables() -> Dict[str, bool]:
    """Validate required environment variables"""
    required_vars = [
        'AWS_REGION',
        'AGENT_S3_BUCKET',
        'ELASTICACHE_ENDPOINT'
    ]
    
    validation_results = {}
    for var in required_vars:
        value = os.getenv(var)
        validation_results[var] = bool(value and value.strip())
        if not validation_results[var]:
            logger.warning(f"Environment variable {var} is not set or empty")
    
    return validation_results

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text (simple implementation)"""
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
        'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Extract words
    words = text.lower().split()
    keywords = []
    
    for word in words:
        # Remove punctuation
        clean_word = ''.join(char for char in word if char.isalnum())
        
        # Filter by length and stop words
        if len(clean_word) >= min_length and clean_word not in stop_words:
            keywords.append(clean_word)
    
    return list(set(keywords))  # Remove duplicates

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity based on common keywords"""
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 and not keywords2:
        return 1.0
    
    if not keywords1 or not keywords2:
        return 0.0
    
    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)
    
    return len(intersection) / len(union) if union else 0.0

def retry_with_backoff(func, max_attempts: int = 3, backoff_multiplier: float = 2.0):
    """Decorator for retrying functions with exponential backoff"""
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    wait_time = backoff_multiplier ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_attempts} attempts failed")
        
        raise last_exception
    
    return wrapper

def health_check() -> Dict[str, Any]:
    """Perform health check on all services"""
    health_status = {
        'timestamp': get_current_timestamp(),
        'overall_status': 'healthy',
        'services': {}
    }
    
    # Check environment variables
    env_validation = validate_environment_variables()
    health_status['services']['environment'] = {
        'status': 'healthy' if all(env_validation.values()) else 'degraded',
        'details': env_validation
    }
    
    # Check DynamoDB
    try:
        aws_manager.dynamodb.meta.client.describe_limits()
        health_status['services']['dynamodb'] = {'status': 'healthy'}
    except Exception as e:
        health_status['services']['dynamodb'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['overall_status'] = 'degraded'
    
    # Check S3
    try:
        aws_manager.s3.list_buckets()
        health_status['services']['s3'] = {'status': 'healthy'}
    except Exception as e:
        health_status['services']['s3'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['overall_status'] = 'degraded'
    
    # Check Redis
    try:
        if aws_manager.redis_client:
            aws_manager.redis_client.ping()
            health_status['services']['redis'] = {'status': 'healthy'}
        else:
            health_status['services']['redis'] = {'status': 'unavailable'}
    except Exception as e:
        health_status['services']['redis'] = {'status': 'unhealthy', 'error': str(e)}
    
    return health_status

# Performance monitoring utilities
class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        logger.info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.utcnow()
        duration = (self.end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.info(f"Completed operation: {self.operation_name} in {format_duration(duration)}")
        else:
            logger.error(f"Failed operation: {self.operation_name} after {format_duration(duration)}")
    
    @property
    def duration(self) -> Optional[float]:
        """Get operation duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None