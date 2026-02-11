# Incident Response Guide

## Overview

This guide defines the severity levels, escalation procedures, and response protocols for incidents affecting the Release Manager service. All incidents must be tracked and documented according to this guide.

## Severity Levels

Incidents are classified into four severity levels based on user impact and system criticality:

### P1 - Critical

**Definition**: Service completely unavailable or data loss occurring. User-facing functionality is completely broken.

**Characteristics**:
- Complete service outage (100% user impact)
- Data corruption or permanent data loss
- Security breach or unauthorized access
- Payment processing completely down
- Production database offline

**Response Time**: Immediate (< 5 minutes)
**Response Team**: VP Engineering, Engineering Manager, On-Call Engineer, DevOps Lead
**Communication**: Continuous updates every 5 minutes to stakeholders

**Actions**:
1. Page entire on-call team immediately
2. Initiate incident bridge call (see communication templates below)
3. Focus on immediate stabilization
4. Prepare rollback decision within 15 minutes
5. Execute rollback or fix with 30-minute decision deadline

**Example Incidents**:
- Production API completely down after deployment
- Database corruption losing user data
- Security vulnerability allowing unauthorized access to user accounts
- Authentication service completely unavailable

### P2 - High

**Definition**: Significant feature broken or severe degradation affecting majority of users. Partial service outage.

**Characteristics**:
- Major feature completely broken (> 25% user impact)
- Service slow but operational (response times > 5 seconds)
- Data inaccessible but not corrupted
- Workaround exists but requires manual intervention
- Database connections maxed out

**Response Time**: 15 minutes or less
**Response Team**: Engineering Manager, On-Call Engineer, DevOps Lead
**Communication**: Updates every 15-30 minutes

**Actions**:
1. Page on-call engineer and engineering manager
2. Create incident ticket and post to #incidents Slack channel
3. Investigate root cause (target: 30 minutes)
4. Implement fix or rollback (target: 60 minutes)
5. Monitor for stability (target: 30 minutes post-fix)

**Example Incidents**:
- Release history not loading for users
- Deployment creation API returning 500 errors
- Database queries timing out during peak traffic
- Cache layer down causing slow response times

### P3 - Medium

**Definition**: Minor feature broken or noticeable degradation affecting small subset of users. Workaround available.

**Characteristics**:
- Single feature not working (< 10% user impact)
- Intermittent errors for some users
- Performance degradation during specific operations
- Non-critical functionality broken
- Retry succeeds after transient error

**Response Time**: 1 hour
**Response Team**: On-Call Engineer
**Communication**: Updates every 1-2 hours

**Actions**:
1. Create incident ticket
2. Investigate root cause (target: 2 hours)
3. Implement fix during next scheduled deployment (target: next day)
4. Monitor logs for similar errors
5. Plan permanent fix for next sprint

**Example Incidents**:
- Notification delivery failing for some users
- Specific report view returning incorrect data
- API rate limiting triggering for legitimate traffic
- Search feature slow for large deployments

### P4 - Low

**Definition**: Cosmetic issues or minor bugs. No user impact or inconvenience easily worked around.

**Characteristics**:
- UI display issue not affecting functionality
- Typo or minor wording problem
- Non-critical feature unavailable
- User can easily work around issue
- Affects only internal tooling

**Response Time**: None (schedule for next sprint)
**Response Team**: Standard development process
**Communication**: Log in issue tracker

**Actions**:
1. Create issue in project management system
2. Add to backlog for next planning cycle
3. Assign priority based on impact
4. Include in next planned release

**Example Incidents**:
- Button label spelling error
- Dashboard widget layout incorrect
- Email formatting issue
- Deprecated API endpoint still functional but showing warnings

## Escalation Matrix

Use this matrix to determine who to contact based on incident severity and time:

| Severity | < 30 min | 30-60 min | > 60 min |
|----------|----------|-----------|----------|
| P1 | VP Engineering, All on-call | + CTO | + CEO |
| P2 | Engineering Manager, On-call | + VP Engineering | + VP Engineering |
| P3 | On-call Engineer | + Engineering Manager | + VP Engineering |
| P4 | Development team | - | - |

**On-Call Schedule**: https://pagerduty.company.com/escalation_policies
**Emergency Contacts**: See [Deployment Guide](./deployment-guide.md#emergency-contacts)

## Communication Templates

### Incident Bridge Call Setup

Use this template to initiate the incident response bridge:

```
SUBJECT: Page XYZ is down - Join incident bridge

BODY:
Please join the incident bridge immediately.

Zoom: https://zoom.us/j/[INCIDENT_NUMBER]
Slack: #incidents

Incident Details:
- Severity: P[1-4]
- Service: Release Manager
- Symptoms: [Brief description]
- Impact: [Number of affected users or features]
- Started: [Timestamp]

Action Items:
1. Acknowledge incident
2. Identify scope
3. Implement mitigation
```

### Initial Notification to Stakeholders

Post this template to #incidents and email stakeholders:

```markdown
# INCIDENT: Release Manager API Degradation

**Severity**: P2
**Service**: Release Manager API
**Status**: INVESTIGATING
**Started**: 2024-01-15 14:30 UTC

## Summary
API response times increased to 5-10 seconds. Approximately 30% of requests timing out.

## Impact
- Users unable to create new releases
- Release history loading slowly
- Estimated 500+ users affected

## Timeline
- 14:30 UTC: First alert triggered
- 14:32 UTC: Incident confirmed
- 14:35 UTC: Engineering team notified
- 14:40 UTC: Root cause investigation started

## Current Actions
1. Investigating recent deployment
2. Analyzing database performance metrics
3. Preparing rollback decision

## Next Update
In 15 minutes or when status changes

**Lead**: [Engineer Name] @[slack_handle]
**Slack Channel**: #incidents
**Bridge**: [Zoom link]
```

### Incident Resolved Notification

```markdown
# INCIDENT RESOLVED: Release Manager API Degradation

**Severity**: P2
**Service**: Release Manager API
**Status**: RESOLVED
**Duration**: 45 minutes (14:30 - 15:15 UTC)

## Root Cause
Recent deployment included inefficient database query that caused connection pool exhaustion.

## Resolution
Rolled back deployment to v2024.01.14 at 14:55 UTC. Applied code fix and redeployed at 15:10 UTC.

## Timeline
- 14:30 UTC: Issue detected
- 14:35 UTC: Team notified
- 14:55 UTC: Rollback executed
- 15:10 UTC: Fixed version deployed
- 15:15 UTC: All metrics normalized

## Impact
- Total downtime: 45 minutes
- Users affected: ~500
- Transactions lost: 0 (none pending)

## Post-Mortem
Post-mortem meeting scheduled for [DATE/TIME] to discuss:
- How to catch inefficient queries in code review
- Performance testing improvements
- Deployment procedure updates

**Thank you for your patience.**
```

## Investigation Steps

### 1. Initial Assessment (5 minutes)

Gather baseline information about the incident:

```bash
# Check service status
curl -s https://api.internal/health | jq .

# Check recent deployments
kubectl rollout history deployment/release-manager-prod -n production

# View recent pod events
kubectl describe deployment release-manager-prod -n production

# Check error rate
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=rate(errors_total[5m])'

# Check response times
curl -s 'http://prometheus:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.99, rate(request_duration_seconds_bucket[5m]))'
```

### 2. Log Analysis (10-15 minutes)

Review application logs for error patterns:

```bash
# Recent errors (last 100 lines)
kubectl logs deployment/release-manager-prod -n production --tail=100 | grep ERROR

# Error spike timeline
kubectl logs deployment/release-manager-prod -n production --since=1h | grep -c ERROR

# Specific error type search
kubectl logs deployment/release-manager-prod -n production --tail=500 | \
  grep "database connection\|timeout\|OOM"

# Error rate by endpoint
kubectl logs deployment/release-manager-prod -n production --tail=1000 | \
  grep "ERROR\|WARN" | awk '{print $NF}' | sort | uniq -c | sort -rn
```

### 3. Database Investigation (10-15 minutes)

Check database performance and connections:

```bash
# Active connections
POD_NAME=$(kubectl get pod -l app=db -n production -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD_NAME -n production -- psql -U postgres -d release_manager -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Long-running queries
kubectl exec -it $POD_NAME -n production -- psql -U postgres -d release_manager -c \
  "SELECT query, query_start FROM pg_stat_activity \
   WHERE state != 'idle' ORDER BY query_start;"

# Slow query log
kubectl exec -it $POD_NAME -n production -- psql -U postgres -d release_manager -c \
  "SELECT query, mean_time, calls FROM pg_stat_statements \
   ORDER BY mean_time DESC LIMIT 10;"

# Table/index bloat
kubectl exec -it $POD_NAME -n production -- psql -U postgres -d release_manager -c \
  "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) \
   FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
```

### 4. Resource Analysis (10 minutes)

Check resource utilization on affected pods:

```bash
# Pod resource usage
kubectl top pods -n production -l app=release-manager

# Detailed pod metrics
kubectl get pods -n production -l app=release-manager -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].resources.requests}{"\t"}{.spec.containers[0].resources.limits}{"\n"}{end}'

# Check for OOM events
kubectl describe nodes | grep -A 5 "memory"

# Disk space usage
kubectl exec -it $(kubectl get pod -l app=release-manager -n production \
  -o jsonpath='{.items[0].metadata.name}') -n production \
  -- df -h
```

### 5. Deployment History (5 minutes)

Review recent changes:

```bash
# Last 5 deployments
kubectl rollout history deployment/release-manager-prod -n production | head -10

# Detailed deployment information
kubectl get deployment release-manager-prod -n production -o yaml

# Compare with previous version
git diff v2024.01.14..v2024.01.15
```

## Resolution Checklist

Follow this checklist to confirm incident is resolved:

### Immediate Resolution (for P1/P2)

- [ ] Service responding to health checks
- [ ] Error rate returned to normal (< 0.1% of requests)
- [ ] Response times normalized to pre-incident levels
- [ ] No pods in CrashLoopBackOff state
- [ ] Database connections normalized
- [ ] User reports of issues ceased
- [ ] All metrics on monitoring dashboard green

### Extended Resolution (within 1 hour)

- [ ] Full regression test suite passed
- [ ] Integration tests with external services passed
- [ ] Database data integrity verified
- [ ] Cache consistency verified
- [ ] Logs reviewed for any outstanding errors
- [ ] All team members aware incident is resolved

### Follow-Up Resolution (within 24 hours)

- [ ] Post-mortem conducted
- [ ] Root cause document completed
- [ ] Action items assigned
- [ ] Code review completed for permanent fix
- [ ] Monitoring improvements implemented
- [ ] Team training scheduled if needed

## Post-Mortem Template

Schedule post-mortem within 48 hours of P1/P2 incidents:

```markdown
# Post-Mortem: Release Manager API Degradation

**Date**: 2024-01-15
**Duration**: 45 minutes
**Severity**: P2
**Lead**: [Engineer Name]
**Attendees**: [List of team members]

## Summary
[1-2 sentence description of what happened]

## Impact
- **Users Affected**: ~500
- **Duration**: 45 minutes
- **Data Lost**: None
- **Revenue Impact**: $0 (internal tool)

## Timeline

| Time | Event |
|------|-------|
| 14:30 | Error rate spike detected by monitoring |
| 14:32 | Alert triggered and on-call notified |
| 14:35 | Incident confirmed, bridge call started |
| 14:40 | Root cause identified (N+1 queries) |
| 14:55 | Rollback executed |
| 15:10 | Fixed version redeployed |
| 15:15 | All metrics normalized |

## Root Cause Analysis

The recent deployment included changes to the release history endpoint that introduced an N+1 query problem. Each release in the list was triggering a separate database query to fetch deployment details, causing massive load on the database.

```python
# Problematic code
for release in releases:
    deployments = db.query(Deployment).filter_by(release_id=release.id)  # N+1!
```

**Why it wasn't caught**: The test environment has only 10 releases, so the N+1 problem wasn't apparent. Production has 5,000+ releases.

## Action Items

| Item | Owner | Due Date | Priority |
|------|-------|----------|----------|
| Fix N+1 query with JOIN | @engineer_name | 2024-01-16 | High |
| Add query count test | @qa_name | 2024-01-17 | High |
| Performance test with prod-like data | @devops_name | 2024-01-18 | Medium |
| Code review standards update | @manager_name | 2024-01-20 | Medium |

## Preventative Measures

1. **Code Review Process**: Require database query review for endpoints that touch many rows
2. **Testing**: Add performance tests using production-like datasets (1000+ records)
3. **Monitoring**: Add alert for database query count spikes
4. **Deployment**: Canary deploy to detect performance issues on 1% of traffic first

## Lessons Learned

- **What Went Well**: Quick detection and rollback prevented extended outage
- **What Could Improve**: Performance testing should use realistic data volumes
- **Key Insight**: Test environments don't reflect production scale

## Approval

Engineering Manager: ________________  Date: __________
VP Engineering: ________________  Date: __________
```

## Related Documentation

- [Deployment Guide](./deployment-guide.md) - How deployments relate to incidents
- [Rollback Procedure](./rollback-procedure.md) - Emergency rollback procedures
- [Database Migrations](./database-migrations.md) - Migration-related incidents
