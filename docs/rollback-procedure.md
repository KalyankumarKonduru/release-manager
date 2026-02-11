# Rollback Procedure

## Overview

Rollback is the process of reverting to the previous stable version of the application. This document outlines when to rollback, how rollback is triggered, and verification steps to ensure successful rollback.

## When to Rollback

Initiate rollback immediately if any of the following conditions are detected post-deployment:

**Critical Error Indicators**
- Application error rate exceeds 5% for more than 2 minutes
- Unhandled exceptions appearing in logs at high frequency
- API response time p99 exceeds 2 seconds
- Application fails liveness probe and pods enter crash loop

**Health Check Failures**
- `/health` endpoint returns non-200 status
- Database connectivity check fails
- Cache layer becomes unavailable
- Message queue connection drops

**User-Reported Issues**
- Multiple user reports of functionality not working within 5 minutes of deployment
- Data corruption or loss reported by users
- Security vulnerability discovered in newly deployed code
- Payment processing failures or financial data issues

**Infrastructure Issues**
- Resource exhaustion (memory, CPU, disk) on deployed pods
- Network connectivity issues preventing external dependencies
- Persistent pod restart loops despite resource availability

## Automatic Rollback Triggers

The system is configured to automatically rollback under specific conditions without manual intervention:

```yaml
# Kubernetes deployment configuration
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  progressDeadlineSeconds: 600

  # Liveness probe trigger
  livenessProbe:
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 30
    periodSeconds: 10
    failureThreshold: 3
    timeoutSeconds: 5

  # Readiness probe trigger
  readinessProbe:
    httpGet:
      path: /ready
      port: 8080
    initialDelaySeconds: 10
    periodSeconds: 5
    failureThreshold: 2
    timeoutSeconds: 5
```

**Automatic Rollback Conditions**
- Pod fails liveness probe 3 consecutive times (30 seconds total)
- Pod fails readiness probe 2 consecutive times (10 seconds total)
- Deployment fails to progress within 10 minutes
- All pods in deployment enter CrashLoopBackOff state

When automatic rollback occurs, an alert is triggered in PagerDuty and Slack notifications are sent to the #incidents channel.

## Manual Rollback Procedure

If automatic rollback does not occur or if you need to manually rollback, follow these steps:

### Step 1: Assess the Situation (1-2 minutes)

Before initiating rollback, gather information about the issue:

```bash
# Check current deployment status
kubectl get deployment release-manager-prod -n production -o wide

# View recent pod events
kubectl describe deployment release-manager-prod -n production

# Check pod restart count
kubectl get pods -n production -l app=release-manager -o custom-columns=\
NAME:.metadata.name,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount

# Examine logs for errors
kubectl logs deployment/release-manager-prod -n production --tail=200 | grep ERROR
```

### Step 2: Notify Stakeholders (1 minute)

Inform relevant teams before executing rollback:

- **Slack**: Post to #incidents: "Initiating rollback of Release Manager to previous version due to [brief reason]. ETA: 5 minutes"
- **Engineering Manager**: Notify via Slack or phone call
- **Monitoring**: Alert monitoring team to expect metric fluctuations during rollback

### Step 3: Execute Rollback (2-3 minutes)

Use kubectl's rollout undo command to revert to the previous deployment:

```bash
# View rollout history
kubectl rollout history deployment/release-manager-prod -n production

# Example output:
# deployment.apps/release-manager-prod
# REVISION  CHANGE-CAUSE
# 8         Release v2024.01.14
# 9         Release v2024.01.15 (current)

# Undo to previous revision
kubectl rollout undo deployment/release-manager-prod \
  --to-revision=8 \
  -n production

# Monitor rollout progress (should complete in 2-3 minutes)
kubectl rollout status deployment/release-manager-prod -n production --timeout=5m
```

### Step 4: Verify Rollback Success (3-5 minutes)

Execute comprehensive verification to confirm rollback completed successfully:

**Pod Status Check**
```bash
# All pods should be Running and Ready
kubectl get pods -n production -l app=release-manager

# No pods should be restarting
kubectl get pods -n production -l app=release-manager -o json | \
  jq '.items[].status.containerStatuses[].restartCount'
```

**Application Health Check**
```bash
# Should return HTTP 200 with healthy status
curl -v https://api.internal/health
```

**Database Connectivity**
```bash
# Check that database migrations are at previous version
POD_NAME=$(kubectl get pod -l app=release-manager -n production \
  -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD_NAME -n production -- alembic current
```

**Smoke Tests**
```bash
# Run smoke tests to verify basic functionality
./tests/smoke-tests.sh --environment production

# Run critical path tests
./tests/integration-tests.sh --environment production --suite critical-path
```

**Metrics Verification**
```bash
# Error rate should drop below 1%
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=rate(errors_total[5m])'

# Response time should normalize to pre-deployment levels
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.99, rate(request_duration_seconds_bucket[5m]))'
```

## Database Migration Rollback

If the deployment included database migrations, additional steps are required:

### Automatic Migration Rollback

If a migration caused the deployment failure, Kubernetes will automatically revert the previous schema changes:

```bash
# Check current migration version before rollback
POD_NAME=$(kubectl get pod -l app=release-manager -n production \
  -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD_NAME -n production -- alembic current

# Output example:
# Running stamp_revision ---> 9c2b3f1a4e5d
```

### Manual Migration Rollback

If automatic rollback fails or migrations must be manually reverted:

```bash
# Determine previous migration revision
git log --oneline -n 20 | grep -i migration

# SSH into database pod (if required)
kubectl exec -it $(kubectl get pod -l app=db -n production \
  -o jsonpath='{.items[0].metadata.name}') -n production -- bash

# Execute migration downgrade (example for one revision back)
alembic downgrade -1

# Verify migration version
alembic current

# Verify schema integrity
psql -U postgres -d release_manager -c "\dt"
```

**Critical**: Before executing migration rollback, confirm the previous schema is still present and valid in the database.

### Data Cleanup After Rollback

If new database schema was introduced and rolled back, cleanup orphaned data:

```bash
# Connect to database
kubectl exec -it $(kubectl get pod -l app=db -n production \
  -o jsonpath='{.items[0].metadata.name}') -n production -- psql

# Inside psql:
-- Drop any temporary tables created by migration
DROP TABLE IF EXISTS schema_migrations_temp;

-- Vacuum to reclaim space
VACUUM FULL;

-- Verify data consistency
SELECT * FROM release_deployments LIMIT 5;
```

## Post-Rollback Verification

After successful rollback, perform these additional checks:

### Data Integrity Checks (5-10 minutes)

```bash
# Run data consistency checks
./scripts/verify-data-integrity.sh

# Check for orphaned records from failed deployment
./scripts/check-orphaned-records.sh

# Verify audit logs are consistent
./scripts/audit-log-consistency.sh
```

### User-Facing Verification (5 minutes)

- Test login functionality
- Verify deployment history display
- Confirm release notes are accessible
- Check that previous releases are still visible
- Verify API endpoints respond correctly

### Monitoring Dashboard Review (5 minutes)

- Error rate should return to normal levels (< 0.1%)
- Response times should match previous deployment
- Resource utilization should normalize
- No new alerts should be firing

## Incident Report Template

After completing rollback, document the incident:

```markdown
# Incident Report: Rollback of v2024.01.15

## Summary
[Brief description of what happened]

## Timeline
- **14:30 UTC**: Deployment of v2024.01.15 to production
- **14:35 UTC**: Error rate spike detected (8% of requests)
- **14:36 UTC**: Automatic rollback initiated by Kubernetes
- **14:39 UTC**: Rollback verification complete, application stable

## Root Cause
[Description of why the deployment failed]

## Immediate Actions Taken
1. Executed automatic rollback to v2024.01.14
2. Verified application health post-rollback
3. Notified stakeholders via Slack
4. Opened incident ticket for investigation

## Investigation Results
[Detailed findings from post-mortems and testing]

## Resolution
[How the issue was fixed in code review]

## Prevention
[Process improvements to prevent similar incidents]

## Follow-up Items
- [ ] Code review identified specific issue by [engineer]
- [ ] Tests added to catch regression by [date]
- [ ] Documentation updated by [date]

## Severity Level
P2 - Deployment failed but successfully rolled back with no user impact

## Assigned To
[Engineer responsible for fix]

## Approval
Release Manager: ________________  Date: __________
Engineering Manager: ________________  Date: __________
```

## Related Documentation

- [Deployment Guide](./deployment-guide.md) - Complete deployment procedures
- [Incident Response Guide](./incident-response.md) - How to handle post-deployment incidents
- [Database Migrations](./database-migrations.md) - Migration procedures and rollback strategies
