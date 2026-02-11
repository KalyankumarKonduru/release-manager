# Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Release Manager application to development, staging, and production environments. Always follow the pre-deployment checklist before proceeding with any deployment.

## Pre-Deployment Checklist

Before initiating any deployment, verify the following items are complete:

**Code & Testing**
- [ ] All changes merged to the main branch
- [ ] All automated tests passing (unit, integration, e2e)
- [ ] Code review completed and approved
- [ ] No known failing tests or TODO items in deployment-blocking code
- [ ] Git tags created for the release version

**Documentation & Planning**
- [ ] Deployment plan documented (estimated duration, rollback plan)
- [ ] Release notes prepared with breaking changes clearly marked
- [ ] Database migration strategy reviewed (if applicable)
- [ ] Architecture changes documented and validated

**Approvals & Communication**
- [ ] Deployment approval obtained from release manager
- [ ] Maintenance window scheduled (if required)
- [ ] Stakeholders notified of deployment timeline
- [ ] On-call engineer confirmed and available
- [ ] Incident response team on standby for critical deployments

**Infrastructure & Monitoring**
- [ ] Target environment health verified
- [ ] Database backups completed
- [ ] Monitoring dashboards and alert rules verified
- [ ] Log aggregation system operational
- [ ] Rollback procedure tested and verified

## Deployment to Development Environment

The development environment is used for initial testing and validation. Deployments here can occur multiple times daily with minimal ceremony.

```bash
# 1. Switch to the release-manager repository
cd /path/to/release-manager

# 2. Build Docker image for development
docker build -t release-manager:dev-$(git rev-parse --short HEAD) .

# 3. Push to development registry
docker push release-manager:dev-$(git rev-parse --short HEAD)

# 4. Update development deployment manifest
kubectl set image deployment/release-manager-dev \
  release-manager=release-manager:dev-$(git rev-parse --short HEAD) \
  -n development

# 5. Monitor rollout
kubectl rollout status deployment/release-manager-dev -n development
```

**Verification**
- Confirm pods are running: `kubectl get pods -n development`
- Check application logs: `kubectl logs -f deployment/release-manager-dev -n development`
- Verify API endpoint: `curl http://dev-api.internal/health`

## Deployment to Staging Environment

Staging mirrors production configuration and is used for comprehensive testing before production deployment. Require explicit approval before proceeding.

```bash
# 1. Tag the release
git tag -a v$(date +%Y.%m.%d.%H%M%S) -m "Release for staging deployment"
git push origin --tags

# 2. Build Docker image for staging
docker build -t release-manager:staging-$(git rev-parse --short HEAD) .

# 3. Push to staging registry
docker push release-manager:staging-$(git rev-parse --short HEAD)

# 4. Apply any database migrations (if needed)
kubectl exec -it $(kubectl get pod -l app=release-manager -n staging \
  -o jsonpath='{.items[0].metadata.name}') -n staging \
  -- alembic upgrade head

# 5. Update staging deployment
kubectl set image deployment/release-manager-staging \
  release-manager=release-manager:staging-$(git rev-parse --short HEAD) \
  -n staging

# 6. Monitor the rollout
kubectl rollout status deployment/release-manager-staging -n staging --timeout=5m
```

**Verification**
- Confirm deployment successful: `kubectl get deployment release-manager-staging -n staging`
- Check application health: `curl https://staging-api.internal/health`
- Run smoke tests: `./tests/smoke-tests.sh --environment staging`
- Verify database migrations: `kubectl exec -it $(kubectl get pod -l app=release-manager -n staging -o jsonpath='{.items[0].metadata.name}') -n staging -- alembic current`

## Deployment to Production Environment

Production deployments require careful coordination and multiple verification steps. Plan for a 30-minute maintenance window.

```bash
# 1. Create release branch and tag
git checkout -b release/v$(date +%Y.%m.%d)
git tag -a v$(date +%Y.%m.%d) -m "Production release"

# 2. Build and push production image
docker build -t release-manager:prod-$(git rev-parse --short HEAD) .
docker push release-manager:prod-$(git rev-parse --short HEAD)

# 3. Perform database migrations in safe mode
kubectl exec -it $(kubectl get pod -l app=release-manager -n production \
  -o jsonpath='{.items[0].metadata.name}') -n production \
  -- alembic upgrade head --sql > migration-output.sql

# Review the migration SQL:
cat migration-output.sql

# 4. Apply database migrations
kubectl exec -it $(kubectl get pod -l app=release-manager -n production \
  -o jsonpath='{.items[0].metadata.name}') -n production \
  -- alembic upgrade head

# 5. Deploy using canary strategy (10% → 50% → 100%)
kubectl patch deployment release-manager-prod \
  -p '{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxSurge":1,"maxUnavailable":0}}}}' \
  -n production

kubectl set image deployment/release-manager-prod \
  release-manager=release-manager:prod-$(git rev-parse --short HEAD) \
  -n production

# 6. Monitor rollout progress
kubectl rollout status deployment/release-manager-prod -n production --timeout=10m
```

**Verification Steps**

After deployment, execute the following verification steps in order:

1. **Pod Health (0-2 minutes)**
   ```bash
   kubectl get pods -n production -l app=release-manager
   kubectl logs deployment/release-manager-prod -n production --tail=100
   ```

2. **API Endpoint Health (2-5 minutes)**
   ```bash
   for i in {1..10}; do
     curl -s https://api.internal/health | jq .
     sleep 2
   done
   ```

3. **Smoke Tests (5-10 minutes)**
   ```bash
   ./tests/smoke-tests.sh --environment production --verbose
   ```

4. **Integration Tests (10-15 minutes)**
   ```bash
   ./tests/integration-tests.sh --environment production
   ```

5. **Monitor Key Metrics (ongoing)**
   - Error rate: `prometheus query 'rate(errors_total[5m])'`
   - Response time: p99 < 500ms
   - Database connections: < 80 of max pool
   - Memory usage: < 70% of allocated

## Health Check Verification

Perform health checks at each stage of deployment to ensure the application is functioning correctly.

**Endpoint: `/health`** - Returns application health status
```bash
curl -s https://api.internal/health | jq .
```

Expected response:
```json
{
  "status": "healthy",
  "version": "v2024.01.15",
  "timestamp": "2024-01-15T14:30:00Z",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "message_queue": "ok"
  }
}
```

**Endpoint: `/metrics`** - Prometheus metrics endpoint
```bash
curl -s https://api.internal/metrics | grep release_manager
```

Monitor these critical metrics:
- `release_manager_requests_total` - Total request count
- `release_manager_request_duration_seconds` - Request latency
- `release_manager_errors_total` - Error count by type
- `release_manager_db_connections_active` - Active database connections

## Post-Deployment Monitoring

Following successful deployment, monitor the application continuously for 1 hour to catch any issues.

**Dashboard Checks**
- Open Grafana: https://grafana.internal
- Navigate to Release Manager dashboard
- Verify all metrics are trending normally
- Check for any alert triggers

**Log Analysis**
- Access Elasticsearch: https://logs.internal
- Filter for deployment timestamp: `@timestamp > now-1h`
- Search for error patterns: `level:ERROR service:release-manager`
- Review any warnings: `level:WARN service:release-manager`

**Key Metrics to Monitor**
- P99 latency should not exceed 500ms
- Error rate should be < 0.1% of total requests
- Cache hit rate should exceed 85%
- Database query time p99 < 100ms

## Emergency Contacts

In case of deployment issues, contact the following individuals in order:

| Role | Name | Phone | Slack |
|------|------|-------|-------|
| Release Manager | John Smith | +1-555-0100 | @john.smith |
| DevOps Lead | Sarah Chen | +1-555-0101 | @sarah.chen |
| On-Call Engineer | (varies) | See PagerDuty | @on-call |
| Engineering Manager | Mike Johnson | +1-555-0102 | @mike.johnson |

**Escalation Procedure**
1. Contact the Release Manager immediately if deployment fails
2. If no response within 15 minutes, page the On-Call Engineer
3. If critical issue affecting users, declare incident and activate incident response team
4. Document all actions in incident tracking system

## Rollback Procedure

If deployment fails verification or introduces critical issues, see the [Rollback Procedure](./rollback-procedure.md) documentation for detailed steps.

Quick rollback command:
```bash
kubectl rollout undo deployment/release-manager-prod -n production
kubectl rollout status deployment/release-manager-prod -n production --timeout=5m
```
