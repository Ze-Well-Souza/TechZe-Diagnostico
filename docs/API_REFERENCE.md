# 📡 API Reference - TechZe-Diagnostico

## 🌐 Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://techze-diagnostic-backend.onrender.com`

## 🔐 Authentication

### Headers
```http
Content-Type: application/json
Authorization: Bearer {token}
```

## 📊 Core Endpoints

### Health Check
```http
GET /health
```

**Response 200:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-06T12:00:00Z",
  "services": {
    "database": "connected",
    "cache": "active",
    "monitoring": "operational"
  }
}
```

### System Info
```http
GET /api/system/info
```

**Response 200:**
```json
{
  "cpu": {
    "model": "Intel Core i7-9700K",
    "cores": 8,
    "frequency": "3.60 GHz",
    "usage": 25.5
  },
  "memory": {
    "total": "16 GB",
    "available": "12 GB",
    "usage": 75.0
  },
  "disk": {
    "total": "500 GB",
    "free": "150 GB", 
    "usage": 70.0
  }
}
```

## 🔍 Diagnostic Endpoints

### Quick Diagnostic
```http
POST /api/v1/diagnostic/quick
```

**Request Body:**
```json
{
  "include_components": ["cpu", "memory", "disk", "network"],
  "detailed": false
}
```

**Response 200:**
```json
{
  "id": "diag-20240106-001",
  "status": "completed",
  "timestamp": "2024-01-06T12:00:00Z",
  "duration": "00:00:45",
  "results": {
    "cpu": {
      "health": 85,
      "status": "good",
      "temperature": 45,
      "issues": []
    },
    "memory": {
      "health": 92,
      "status": "excellent", 
      "usage": 68,
      "issues": []
    },
    "disk": {
      "health": 78,
      "status": "warning",
      "space_usage": 85,
      "issues": ["Low disk space on C:"]
    },
    "network": {
      "health": 95,
      "status": "excellent",
      "connectivity": true,
      "issues": []
    }
  },
  "overall_health": 87,
  "recommendations": [
    "Free up disk space on C: drive",
    "Consider adding more storage"
  ]
}
```

### Detailed Diagnostic
```http
POST /api/v1/diagnostic/detailed
```

**Request Body:**
```json
{
  "components": {
    "cpu": {
      "stress_test": true,
      "benchmark": true
    },
    "memory": {
      "full_scan": true,
      "pattern_test": true
    },
    "disk": {
      "bad_sector_scan": true,
      "performance_test": true
    }
  },
  "notification_url": "https://your-app.com/webhook"
}
```

### Get Diagnostic
```http
GET /api/v1/diagnostic/{diagnostic_id}
```

**Response 200:**
```json
{
  "id": "diag-20240106-001",
  "status": "completed",
  "created_at": "2024-01-06T12:00:00Z",
  "completed_at": "2024-01-06T12:00:45Z",
  "results": {...},
  "report_url": "/api/v1/diagnostic/diag-20240106-001/report"
}
```

### List Diagnostics
```http
GET /api/v1/diagnostic?limit=10&offset=0&status=completed
```

**Query Parameters:**
- `limit`: Number of results (default: 10, max: 100)
- `offset`: Pagination offset (default: 0)
- `status`: Filter by status (pending, running, completed, failed)
- `date_from`: Filter from date (ISO format)
- `date_to`: Filter to date (ISO format)

**Response 200:**
```json
{
  "total": 150,
  "limit": 10,
  "offset": 0,
  "diagnostics": [
    {
      "id": "diag-20240106-001",
      "status": "completed",
      "created_at": "2024-01-06T12:00:00Z",
      "overall_health": 87
    }
  ]
}
```

## 📋 Report Endpoints

### Generate Report
```http
POST /api/v1/diagnostic/{diagnostic_id}/report
```

**Request Body:**
```json
{
  "format": "pdf",
  "include_charts": true,
  "include_raw_data": false,
  "template": "standard"
}
```

**Response 200:**
```json
{
  "report_id": "report-001",
  "download_url": "/api/v1/reports/report-001/download",
  "format": "pdf",
  "size": "1.2 MB",
  "expires_at": "2024-01-13T12:00:00Z"
}
```

### Download Report
```http
GET /api/v1/reports/{report_id}/download
```

**Response 200:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="diagnostic-report-001.pdf"

[PDF binary data]
```

## ⚡ Performance Endpoints

### Performance Stats
```http
GET /api/v3/performance/stats
```

**Response 200:**
```json
{
  "timestamp": "2024-01-06T12:00:00Z",
  "database_pools": {
    "main_pool": {
      "total_connections": 20,
      "active_connections": 5,
      "idle_connections": 15,
      "health_status": "healthy"
    }
  },
  "query_performance": {
    "total_queries": 1250,
    "avg_execution_time": "0.045s",
    "cache_hit_rate": "78.50%",
    "slow_queries_count": 3
  },
  "cache_stats": {
    "redis_status": "connected",
    "hit_rate": "85.2%",
    "memory_usage": "45 MB"
  }
}
```

### Performance Health
```http
GET /api/v3/performance/health
```

**Response 200:**
```json
{
  "status": "healthy",
  "performance_systems": {
    "connection_pools": "active",
    "query_optimizer": "active", 
    "cache_system": "active"
  },
  "response_time_target": "<200ms",
  "current_load": "optimal",
  "recommendations": []
}
```

### Trigger Optimization
```http
POST /api/v3/performance/optimize
```

**Response 200:**
```json
{
  "message": "Optimization initiated",
  "optimizations_applied": [
    "Query cache refresh",
    "Connection pool rebalancing",
    "Memory cleanup"
  ],
  "estimated_improvement": "15-20% faster response times",
  "completion_time": "2024-01-06T12:05:00Z"
}
```

## 🔧 System Endpoints

### Metrics (Prometheus)
```http
GET /metrics
```

**Response 200:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health"} 1250

# HELP response_time_seconds HTTP response time
# TYPE response_time_seconds histogram
response_time_seconds_bucket{le="0.1"} 950
response_time_seconds_bucket{le="0.5"} 1200
```

## ❌ Error Responses

### Error Format
```json
{
  "error": {
    "code": "DIAGNOSTIC_FAILED",
    "message": "Unable to complete diagnostic",
    "details": "CPU stress test timed out",
    "timestamp": "2024-01-06T12:00:00Z",
    "request_id": "req-123456"
  }
}
```

### Status Codes
- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Invalid or missing token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation error
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - System overloaded

### Common Error Codes
- `INVALID_PARAMETERS`: Request parameters are invalid
- `DIAGNOSTIC_FAILED`: Diagnostic process failed
- `REPORT_GENERATION_FAILED`: Unable to generate report
- `SYSTEM_OVERLOADED`: System is under heavy load
- `RATE_LIMIT_EXCEEDED`: Too many requests

## 📝 Rate Limiting

### Default Limits
- **General API**: 100 requests/minute per IP
- **Diagnostic endpoints**: 10 requests/minute per IP
- **Report generation**: 5 requests/minute per IP

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641472800
```

## 🔄 Webhooks

### Diagnostic Completion
When a diagnostic completes, a webhook can be sent:

**POST to your endpoint:**
```json
{
  "event": "diagnostic.completed",
  "timestamp": "2024-01-06T12:00:00Z",
  "data": {
    "diagnostic_id": "diag-20240106-001",
    "status": "completed",
    "overall_health": 87,
    "report_url": "/api/v1/diagnostic/diag-20240106-001/report"
  }
}
```

## 📚 Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://techze-diagnostic-backend.onrender.com',
  headers: {
    'Authorization': 'Bearer your-token-here'
  }
});

// Quick diagnostic
const runDiagnostic = async () => {
  try {
    const response = await api.post('/api/v1/diagnostic/quick', {
      include_components: ['cpu', 'memory', 'disk']
    });
    console.log('Diagnostic completed:', response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
};
```

### Python
```python
import requests

headers = {'Authorization': 'Bearer your-token-here'}
base_url = 'https://techze-diagnostic-backend.onrender.com'

# Quick diagnostic
response = requests.post(
    f'{base_url}/api/v1/diagnostic/quick',
    json={'include_components': ['cpu', 'memory', 'disk']},
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"Diagnostic ID: {result['id']}")
    print(f"Overall Health: {result['overall_health']}%")
else:
    print(f"Error: {response.status_code}")
```

### cURL
```bash
# Health check
curl -X GET "https://techze-diagnostic-backend.onrender.com/health"

# Quick diagnostic
curl -X POST "https://techze-diagnostic-backend.onrender.com/api/v1/diagnostic/quick" \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{"include_components": ["cpu", "memory", "disk"]}'
```

---

*Atualizado em: 06/01/2025*