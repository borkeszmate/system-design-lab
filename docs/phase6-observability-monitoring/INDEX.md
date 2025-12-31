# Phase 6: Observability & Monitoring - Index

## Overview

**Total Content:** ~50 KB
**Estimated Reading Time:** 90-120 minutes
**Difficulty:** Intermediate

Understanding and debugging distributed systems through metrics, logs, and traces - the three pillars of observability.

---

## 📚 Documents

### [observability-monitoring.md](./observability-monitoring.md) (~50 KB)

**Complete guide to observability and monitoring in distributed systems**

---

## 🎯 Quick Reference

### Three Pillars of Observability

| Pillar | Purpose | Tools | When to Use |
|--------|---------|-------|-------------|
| **Metrics** | What is happening | Prometheus, Grafana | Dashboards, alerts, trends |
| **Logs** | Why it's happening | ELK, Loki, Splunk | Debugging, audit trails |
| **Traces** | Where time is spent | Jaeger, Zipkin | Performance analysis, request flow |

### Metric Types

| Type | Behavior | Examples | PromQL |
|------|----------|----------|--------|
| **Counter** | Only increases | Total requests, errors | `rate(counter[5m])` |
| **Gauge** | Can increase/decrease | Active users, memory | `gauge` |
| **Histogram** | Distribution | Response times | `histogram_quantile()` |
| **Summary** | Pre-calculated quantiles | Latency percentiles | `summary{quantile="0.95"}` |

### Log Levels

| Level | Use Case | Production |
|-------|----------|------------|
| **DEBUG** | Detailed diagnostic info | ❌ Too verbose |
| **INFO** | General events | ✅ Yes |
| **WARNING** | Potential issues | ✅ Yes |
| **ERROR** | Operation failures | ✅ Yes |
| **CRITICAL** | System unstable | ✅ Yes |

---

## 🗺️ Content Map

### Section 1: Three Pillars (~10 KB, 20 min)
- Overview of metrics, logs, and traces
- How they complement each other
- Request journey visualization

### Section 2: Metrics and Monitoring (~20 KB, 40 min)
- **2.1 Types of Metrics**
  - Counters, gauges, histograms, summaries
  - Prometheus client examples

- **2.2 RED Method** (for Services)
  - Requests (rate)
  - Errors (error rate)
  - Duration (latency distribution)

- **2.3 USE Method** (for Resources)
  - Utilization (% busy)
  - Saturation (queued work)
  - Errors (error count)

- **2.4 Golden Signals** (Google SRE)
  - Latency, Traffic, Errors, Saturation
  - Complete implementation example

- **2.5 Prometheus and Grafana**
  - Configuration
  - PromQL queries
  - Dashboard creation

### Section 3: Logging (~10 KB, 20 min)
- **3.1 Structured Logging**
  - JSON format
  - Implementation in Python

- **3.2 Log Levels**
  - When to use each level
  - Best practices

- **3.3 Correlation IDs**
  - Tracking requests across services
  - Context propagation

- **3.4 ELK Stack**
  - Logstash pipeline
  - Elasticsearch queries
  - Kibana dashboards

### Section 4: Distributed Tracing (~10 KB, 20 min)
- **4.1 OpenTelemetry**
  - Instrumentation
  - Trace context propagation
  - Auto-instrumentation

- **4.2 Trace Visualization**
  - Reading trace diagrams
  - Finding bottlenecks

- **4.3 Sampling Strategies**
  - Ratio-based sampling
  - Error-aware sampling
  - Latency-aware sampling

### Section 5: Alerting and On-Call (~10 KB, 20 min)
- **5.1 Alert Design Principles**
  - Actionable, relevant, timely, specific
  - Good vs bad alert examples

- **5.2 Alert Fatigue Prevention**
  - Using `for` clause
  - Grouping alerts
  - Severity levels

- **5.3 On-Call Best Practices**
  - Runbook structure
  - Escalation procedures

- **5.4 Incident Response**
  - Severity levels
  - Incident timeline
  - Post-mortems

---

## ✅ Learning Checklist

### Metrics
- [ ] Understand difference between counters, gauges, histograms
- [ ] Implement Prometheus metrics in an application
- [ ] Write PromQL queries for rate, error rate, latency
- [ ] Apply RED method to a service
- [ ] Apply USE method to resources
- [ ] Implement Golden Signals monitoring
- [ ] Create Grafana dashboards
- [ ] Calculate p95 and p99 latency

### Logging
- [ ] Implement structured logging (JSON)
- [ ] Use appropriate log levels
- [ ] Add correlation IDs to all logs
- [ ] Propagate request IDs across services
- [ ] Set up ELK stack or alternative
- [ ] Write Elasticsearch queries
- [ ] Create log-based alerts
- [ ] Implement log sampling for high-volume services

### Tracing
- [ ] Instrument application with OpenTelemetry
- [ ] Create manual spans for key operations
- [ ] Propagate trace context across HTTP boundaries
- [ ] Set up Jaeger or Zipkin
- [ ] Analyze traces to find bottlenecks
- [ ] Implement sampling strategy
- [ ] Correlate traces with logs and metrics

### Alerting
- [ ] Design actionable alerts
- [ ] Write alert rules in Prometheus
- [ ] Create runbooks for common incidents
- [ ] Implement alert routing and escalation
- [ ] Set up on-call rotation
- [ ] Practice incident response
- [ ] Write post-mortem for an incident

---

## 💡 Key Concepts

### RED Method Formula
```
Request Rate = rate(http_requests_total[5m])
Error Rate = rate(http_errors_total[5m]) / rate(http_requests_total[5m])
Duration (p95) = histogram_quantile(0.95, rate(http_duration_bucket[5m]))
```

### Structured Logging Format
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "error",
  "service": "order-service",
  "request_id": "req-123-456",
  "trace_id": "abc-def-789",
  "message": "Payment failed",
  "context": {
    "order_id": "ORD-123",
    "user_id": "USR-456",
    "error_code": "GATEWAY_TIMEOUT"
  }
}
```

### Trace Context Propagation
```
Request flow:
API Gateway → Order Service → Payment Service

Headers propagated:
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: vendor1=value1,vendor2=value2
```

---

## 🛠️ Hands-On Exercises

### Exercise 1: Implement Metrics
**Time:** 45 minutes
**Difficulty:** Medium

Add Prometheus metrics to a web service:
1. Install prometheus-client library
2. Add counters for requests and errors
3. Add histogram for response times
4. Expose `/metrics` endpoint
5. Verify metrics in Prometheus UI

### Exercise 2: Set Up Structured Logging
**Time:** 30 minutes
**Difficulty:** Easy

Convert application to structured logging:
1. Replace print() with structured logger
2. Add correlation IDs to all log entries
3. Include user_id, request_id in context
4. Set up log levels appropriately
5. Export logs in JSON format

### Exercise 3: Distributed Tracing
**Time:** 60 minutes
**Difficulty:** Hard

Implement OpenTelemetry tracing:
1. Install OpenTelemetry SDK
2. Auto-instrument HTTP library
3. Create manual spans for database queries
4. Set up Jaeger
5. Propagate context between 2 services
6. Analyze a trace with 5+ spans

### Exercise 4: Create Dashboards and Alerts
**Time:** 45 minutes
**Difficulty:** Medium

Build monitoring stack:
1. Set up Prometheus and Grafana
2. Create dashboard with:
   - Request rate graph
   - Error rate graph
   - Latency (p95, p99) graph
   - Active users gauge
3. Create alert for error rate > 5%
4. Test alert by inducing errors

---

## 📊 Monitoring Stack Comparison

### Open Source
| Stack | Metrics | Logs | Traces | Complexity |
|-------|---------|------|--------|------------|
| Prometheus + ELK + Jaeger | ✅ | ✅ | ✅ | High |
| Grafana Stack (Loki + Tempo) | ✅ | ✅ | ✅ | Medium |
| VictoriaMetrics + Loki | ✅ | ✅ | ❌ | Medium |

### Commercial (SaaS)
| Tool | Metrics | Logs | Traces | Cost |
|------|---------|------|--------|------|
| Datadog | ✅ | ✅ | ✅ | $$$$ |
| New Relic | ✅ | ✅ | ✅ | $$$$ |
| Honeycomb | ⚠️ | ✅ | ✅ | $$$ |
| Lightstep | ⚠️ | ❌ | ✅ | $$$ |

---

## 🎓 Prerequisites

**Before starting this phase:**
- Basic understanding of HTTP and APIs
- Familiarity with Python or Go
- Understanding of JSON
- Phase 5 (Reliability) recommended

**Technical setup:**
- Docker and Docker Compose
- Prometheus, Grafana (can use Docker)
- Elasticsearch or similar (optional)

---

## 📈 Progress Tracking

### Estimated Timeline
- **Reading:** 90-120 minutes
- **Hands-on exercises:** 3-4 hours
- **Total:** 4.5-5.5 hours

### Completion Criteria
- [ ] Read all sections
- [ ] Implement metrics in a service
- [ ] Set up structured logging
- [ ] Create at least one distributed trace
- [ ] Build a Grafana dashboard
- [ ] Create at least one alert
- [ ] Write a runbook for an incident

---

## 🔗 Related Topics

**From Other Phases:**
- Phase 5: SLIs/SLOs inform what to monitor
- Phase 2: Microservices need distributed tracing
- Phase 8: CI/CD should monitor deployments

**Next Steps:**
- Integrate monitoring into CI/CD pipeline
- Set up automated anomaly detection
- Implement cost tracking for cloud resources
- Build correlation between business metrics and technical metrics

---

## 📝 Notes

**Important:** Start with metrics, then add logging, then tracing. Don't try to implement everything at once.

**Token Conservation:**
Do not read this file unless the user explicitly asks about observability, monitoring, metrics, logging, tracing, Prometheus, Grafana, ELK, OpenTelemetry, or related topics.
