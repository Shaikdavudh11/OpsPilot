# OpsPilot API Specification

Base URL: `http://localhost:8000`

---

## 1. System Health

### `GET /health`

Returns service health, active AI provider, and timestamp.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "service": "OpsPilot API",
  "version": "1.0.0",
  "environment": "development",
  "ai_provider": "mock",
  "timestamp": "2026-10-10T11:45:00.000Z"
}
```

---

## 2. Demo Scenarios

### `GET /api/demo-scenarios`

Returns the 6 realistic failure scenarios for testing and demonstration.

#### Response `200 OK`
```json
[
  {
    "id": "postgres-conn-refused",
    "title": "PostgreSQL Connection Refused",
    "description": "Production payment service fails to connect to database cluster on port 5432.",
    "category": "Database",
    "environment": "production",
    "service_name": "payment-processor",
    "expected_severity": "high",
    "raw_logs": "..."
  }
]
```

---

## 3. Incident Investigation

### `POST /api/incidents/analyze`

Analyzes raw logs, scrubs sensitive credentials, determines root cause, and persists the analysis.

#### Request Body
```json
{
  "title": "DB Connection Refused",
  "environment": "production",
  "service_name": "billing-api",
  "raw_logs": "org.postgresql.util.PSQLException: Connection to db.prod.internal:5432 refused."
}
```

#### Response `200 OK`
```json
{
  "id": "cd7be479-f3e3-4706-b052-7268cfd90649",
  "title": "PostgreSQL Database Connection Refused",
  "severity": "high",
  "summary": "Service 'billing-api' in production cannot establish a TCP connection to the PostgreSQL database on port 5432.",
  "likely_root_cause": {
    "description": "The target PostgreSQL service is down, listening on a different network interface, or blocked by firewall/security group rules.",
    "confidence": "high",
    "reasoning": "Logs explicitly state TCP connection refused on port 5432."
  },
  "evidence": [
    {
      "source": "log_stream:line_1",
      "finding": "org.postgresql.util.PSQLException: Connection to db.prod.internal:5432 refused."
    }
  ],
  "recommendations": [
    {
      "action": "Check if PostgreSQL daemon is active on the database host.",
      "reason": "Connection refused indicates no process is bound to port 5432.",
      "risk_level": "low",
      "suggested_command": "pg_isready -h db.prod.internal -p 5432"
    }
  ],
  "prevention": [
    {
      "strategy": "Connection Pooling and Health-Check Circuit Breakers",
      "details": "Configure PgBouncer with pool_pre_ping=True to mitigate transient connection drops."
    }
  ],
  "limitations": [
    "Cannot verify remote database process status without host telemetry access."
  ],
  "analyzed_at": "2026-10-10T11:45:05.123Z",
  "redacted_secrets_count": 0
}
```

#### Error Responses
- `422 Unprocessable Entity`: Log input is too short (< 10 chars) or exceeds `MAX_LOG_SIZE_CHARS`.
- `500 Internal Server Error`: Internal processing error with clean generic message.

---

## 4. Incident History

### `GET /api/incidents`
Returns a list of saved incident report summaries.

### `GET /api/incidents/{incident_id}`
Returns the complete analysis report for a given incident UUID.
