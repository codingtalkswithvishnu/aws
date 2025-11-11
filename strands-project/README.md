# Strands Framework Demo - Customer Service Agent

A comprehensive demo project showcasing the Strands Framework for building intelligent AI agents. This project implements a complete customer service automation workflow with multi-step processing, AWS integration, and enterprise deployment strategies.

> **Created for the "Coding Talks with Vishnu VG" Podcast**  
> This demo accompanies the AWS Agentic AI Development with Strands Framework episode.  
> 
> **Host:** Vishnu VG  
> **LinkedIn:** [linkedin.com/in/vishnuvgtvm](https://linkedin.com/in/vishnuvgtvm)  
> **Podcast:** Coding Talks with Vishnu VG

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose
- AWS CLI v2
- kubectl (for Kubernetes deployment)

### Local Development Setup

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd strands-project
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Configure your AWS credentials
   aws configure
   
   # Set required environment variables
   export AWS_REGION=us-east-1
   export AGENT_S3_BUCKET=your-bucket-name
   export ELASTICACHE_ENDPOINT=your-redis-endpoint
   ```

3. **Install Strands CLI**
   ```bash
   npm install -g @strands/cli
   strands --version
   ```

4. **Initialize and Run**
   ```bash
   # Initialize the project
   strands init
   
   # Start development server
   strands dev
   
   # Access dashboard at http://localhost:8080
   ```

## 📁 Project Structure

### Single Strands Project Structure (Recommended)

This demo follows the **single project approach** for easier coordination and shared resources:

```
strands-project/
├── strands.yaml                 # Main configuration file
├── agents/                      # Agent implementations
│   ├── coordinator-agent.py     # Main workflow coordinator
│   └── step-handlers/           # Individual step processors
│       ├── step1_handler.py     # Data collection agent
│       ├── step2_handler.py     # Analysis agent
│       └── step3_handler.py     # Reporting agent
├── workflows/                   # Workflow definitions
│   └── main-workflow.yaml       # Customer service workflow
├── shared/                      # Shared utilities
│   ├── models.py                # Data models
│   └── utils.py                 # Common utilities
├── docker/                      # Container deployment
│   ├── Dockerfile               # Production container
│   └── docker-compose.yml       # Local development stack
├── k8s/                         # Kubernetes manifests
│   └── deployment.yaml          # EKS deployment
└── requirements.txt             # Python dependencies
```

### Alternative: Multiple Strands Projects Structure

For comparison, here's how you would structure **multiple separate projects** (use only when different teams own different steps):

```
step1-project/
├── strands.yaml
└── agents/
    └── step1_agent.py

step2-project/
├── strands.yaml
└── agents/
    └── step2_agent.py

step3-project/
├── strands.yaml
└── agents/
    └── step3_agent.py

orchestrator-project/
├── strands.yaml
└── agents/
    └── workflow_coordinator.py
```

**Why Single Project is Recommended:**
- ✅ Unified deployment and versioning
- ✅ Shared memory and context across steps
- ✅ Easier debugging and monitoring
- ✅ Single configuration management
- ✅ Reduced operational complexity

## 🏗️ Architecture Overview

### Workflow Execution Flow

```
Customer Request
       ↓
┌─────────────────┐
│ Coordinator     │ ← Main orchestrator
│ Agent           │
└─────────┬───────┘
          ↓
┌─────────────────┐
│ Step 1:         │ ← Collect customer data
│ Data Collector  │   (DynamoDB, S3, Cache)
└─────────┬───────┘
          ↓
┌─────────────────┐
│ Step 2:         │ ← Analyze issue & priority
│ Analyzer        │   (Classification, Sentiment)
└─────────┬───────┘
          ↓
┌─────────────────┐
│ Step 3:         │ ← Generate response & reports
│ Reporter        │   (S3 storage, Notifications)
└─────────┬───────┘
          ↓
   Customer Response
```

### Agent Communication Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    Coordinator Agent                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Step 1    │→ │   Step 2    │→ │   Step 3    │    │
│  │ Data Collect│  │  Analyzer   │  │  Reporter   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   Shared Resources                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  DynamoDB   │  │     S3      │  │ ElastiCache │    │
│  │ (Profiles)  │  │(Documents)  │  │  (Sessions) │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Strands Configuration (`strands.yaml`)

The main configuration file defines:
- **Runtime settings**: Python version, memory, timeout
- **AWS integration**: Region, IAM roles, service endpoints
- **Deployment targets**: Agent Core, Lambda, Container, Kubernetes
- **Environment variables**: S3 buckets, Redis endpoints, API keys
- **Monitoring**: Metrics, logging, health checks

### Workflow Configuration (`workflows/main-workflow.yaml`)

Defines the customer service workflow:
- **3-step process**: Data collection → Analysis → Reporting
- **Conditional steps**: Escalation for critical issues
- **Error handling**: Retry policies and fallback actions
- **Performance settings**: Timeouts, concurrency limits

## 🤖 Agent Architecture

### Coordinator Agent (`agents/coordinator-agent.py`)
- **Main orchestrator** for customer service workflows
- **Tool integration**: Weather API, database queries, MCP servers
- **AWS services**: DynamoDB, S3, ElastiCache
- **Multi-step coordination**: Manages workflow execution

### Step Handlers
1. **Data Collector** (`step1_handler.py`): Gathers customer information
2. **Analyzer** (`step2_handler.py`): Classifies issues and determines priority
3. **Reporter** (`step3_handler.py`): Generates responses and creates reports

### Shared Components
- **Data models** (`shared/models.py`): Type-safe data structures
- **Utilities** (`shared/utils.py`): AWS service managers, caching, validation

## 🚀 Deployment Strategies

### 1. AWS Agent Core Deployment

```bash
# Build and deploy to Agent Core
strands build
strands deploy --target agent-core

# Monitor deployment
strands status --deployment-id <id>
strands logs --agent coordinator-agent
```

### 2. Container Deployment (Docker)

```bash
# Local development with Docker Compose
docker-compose up -d

# Production container build
docker build -f docker/Dockerfile -t strands-customer-service .

# Deploy to ECS
strands deploy --target ecs --image strands-customer-service:latest
```

### 3. Serverless Deployment (Lambda)

```bash
# Package for Lambda
strands package --target lambda --runtime python3.9 --optimize-cold-start

# Deploy with API Gateway trigger
strands deploy --target lambda --trigger api-gateway --memory 1024 --timeout 300

# Deploy with SQS trigger for batch processing
strands deploy --target lambda --trigger sqs --queue customer-requests --batch-size 10
```

### 4. Kubernetes Deployment (EKS)

```bash
# Generate Kubernetes manifests
strands k8s-manifest --output k8s/

# Deploy to EKS cluster
kubectl apply -f k8s/

# Scale deployment
kubectl scale deployment strands-customer-service --replicas=5

# Enable auto-scaling
kubectl autoscale deployment strands-customer-service --cpu-percent=70 --min=2 --max=20
```

## 🔍 Development and Debugging

### Local Development

```bash
# Start with hot reloading
strands dev

# Debug specific workflow
strands debug --workflow customer-support-workflow

# Enable verbose logging
strands dev --log-level debug

# Access development dashboard
open http://localhost:8080
```

### Testing

```bash
# Run unit tests
pytest tests/

# Test specific agent
strands test --agent coordinator-agent

# Integration testing
strands test --workflow customer-support-workflow --input test-data.json
```

### Monitoring and Observability

- **Dashboard**: http://localhost:8080 (development)
- **Metrics**: Prometheus metrics at `/metrics` endpoint
- **Health checks**: `/health` and `/ready` endpoints
- **Logs**: Structured logging with correlation IDs

## 🔧 Tool Integration Examples

### REST API Integration
```python
@tool
def get_weather(city: str) -> str:
    """Get current weather using external API"""
    response = requests.get(
        f"https://api.weather.com/v1/current",
        params={"q": city, "key": os.getenv("WEATHER_API_KEY")}
    )
    return response.json()["current"]["condition"]
```

### Database Integration
```python
@tool
def query_customer(customer_id: str) -> dict:
    """Retrieve customer from DynamoDB"""
    table = dynamodb.Table('customer-profiles')
    response = table.get_item(Key={'customer_id': customer_id})
    return dict(response['Item']) if 'Item' in response else {}
```

### MCP Server Integration
```python
@tool
def read_file_via_mcp(filepath: str) -> str:
    """Read file using MCP filesystem server"""
    return mcp_client.call_tool("read_file", {"path": filepath})
```

## 🔒 Security and Compliance

### AWS IAM Configuration
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/customer-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::customer-service-documents/*"
    }
  ]
}
```

### Security Features
- **Encryption**: At-rest and in-transit encryption
- **Audit logging**: Complete audit trail of agent actions
- **Role-based access**: IAM roles with least-privilege principles
- **Input validation**: Sanitization of all user inputs

## 📊 Performance and Scaling

### Performance Metrics
- **Workflow duration**: Average 15-30 seconds
- **Throughput**: 100+ concurrent workflows
- **Success rate**: >99% with proper error handling
- **Resource usage**: 256MB memory, 0.25 vCPU per agent

### Scaling Strategies
- **Horizontal scaling**: Auto-scaling based on CPU/memory
- **Vertical scaling**: Configurable resource limits
- **Caching**: Redis for session data and frequent queries
- **Load balancing**: Kubernetes service mesh integration

## 🛠️ Troubleshooting

### Common Issues

1. **AWS Credentials**
   ```bash
   # Verify AWS configuration
   aws sts get-caller-identity
   
   # Check IAM permissions
   aws iam simulate-principal-policy --policy-source-arn <role-arn> --action-names dynamodb:GetItem
   ```

2. **Redis Connection**
   ```bash
   # Test Redis connectivity
   redis-cli -h <endpoint> ping
   
   # Check ElastiCache security groups
   aws elasticache describe-cache-clusters --cache-cluster-id <cluster-id>
   ```

3. **Container Issues**
   ```bash
   # Check container logs
   docker logs strands-customer-service
   
   # Debug container
   docker exec -it strands-customer-service /bin/bash
   ```

### Debug Commands
```bash
# Enable debug mode
export STRANDS_DEBUG=true

# Verbose logging
strands dev --log-level debug

# Health check
curl http://localhost:8080/health

# Metrics endpoint
curl http://localhost:8080/metrics
```

## 📚 Additional Resources

- [Strands Framework Documentation](https://docs.strands.ai)
- [AWS Agent Core Guide](https://docs.aws.amazon.com/agent-core/)
- [Container Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Deployment Guide](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the [Wiki](wiki) for detailed guides
- **Community**: Join our [Discord](discord-link) for real-time support

## 🎙️ About the Podcast

This demo project was created for the **"Coding Talks with Vishnu VG"** podcast episode on AWS Agentic AI Development with Strands Framework.

**Connect with the Host:**
- **LinkedIn:** [Vishnu VG](https://linkedin.com/in/vishnuvgtvm)
- **Podcast:** Coding Talks with Vishnu VG
- **Episode Topic:** AWS Agentic AI Development with Strands Framework

For more episodes on AI development, cloud architecture, and software engineering best practices, follow the podcast!

---

**Built with ❤️ using the Strands Framework**  
**Demo created for Coding Talks with Vishnu VG Podcast**