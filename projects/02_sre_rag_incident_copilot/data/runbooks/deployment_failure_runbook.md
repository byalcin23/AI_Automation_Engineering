# Deployment Failure Runbook

## Problem Statement
Deployment failures occur when new code cannot be successfully rolled out to production. Common causes include health check failures, database migration issues, configuration errors, or resource constraints.

## Severity Levels
- **Critical**: Production service unavailable after failed deployment
- **High**: Failed deployment with manual rollback required
- **Medium**: Deployment fails but fallback already active
- **Low**: Deployment fails in pre-production or with graceful fallback

## Immediate Actions
1. Assess service impact: Check if users are affected
2. Check deployment status: `kubectl get deployments`, `docker ps`
3. Review recent deployment: `git log --oneline -3`, check deploy logs
4. Get pod/container status: `kubectl describe pod <pod-name>`
5. Check application logs: `kubectl logs <pod-name>`, docker logs

## Diagnosis Steps
1. **Check deployment status**:
   ```bash
   kubectl rollout status deployment/my-app -n production
   kubectl get events -n production --sort-by=.metadata.creationTimestamp
   ```

2. **Check pod status**:
   ```bash
   kubectl get pods -o wide
   kubectl describe pod <pod-name>
   ```

3. **Review logs**:
   ```bash
   kubectl logs <pod-name> --previous
   kubectl logs <pod-name> -c container-name
   ```

4. **Check health endpoints**:
   ```bash
   curl http://service:8080/health
   curl http://service:8080/ready
   ```

5. **Check resources**:
   ```bash
   kubectl top nodes
   kubectl describe node <node-name>
   ```

## Common Causes and Solutions

### Health Check Failures
- **Symptom**: Pod starts but fails liveness/readiness probe
- **Fix**: Check health endpoint, debug application startup
- **Check**: `curl -v http://localhost:8080/health`
- **Logs**: Look for startup errors in application logs

### Database Migration Failed
- **Symptom**: Pod fails during database initialization
- **Fix**: Check migration logs, rollback schema, fix migration script
- **Command**: `kubectl logs <pod> | grep -i migration`
- **Fix**: Revert migration, apply fix, re-run

### Insufficient Resources
- **Symptom**: Pod pending, not enough CPU/memory on cluster
- **Fix**: Scale cluster, adjust resource requests, scale down other services
- **Check**: `kubectl describe node` to see available resources

### Configuration/Secret Issues
- **Symptom**: Pod crashes with config error
- **Fix**: Verify ConfigMaps and Secrets, update values
- **Check**: `kubectl get configmap`, `kubectl get secret`

### Image Pull Failure
- **Symptom**: ImagePullBackOff error
- **Fix**: Verify image exists, check credentials, retry
- **Check**: `kubectl describe pod` for pull error details

### Service Dependency Down
- **Symptom**: Pod starts but cannot connect to database or other service
- **Fix**: Verify dependency is running, check network connectivity
- **Debug**: `kubectl exec -it <pod> -- curl http://dependency:port`

## Recovery Procedures

### Option 1: Rollback Immediately
```bash
kubectl rollout undo deployment/my-app
kubectl rollout status deployment/my-app
```

### Option 2: Fix and Redeploy
```bash
# Fix the issue locally
git commit -am "fix: deployment issue"
git push origin branch-name

# Trigger new deployment
kubectl rollout restart deployment/my-app
```

### Option 3: Manual Verification Then Rollout
```bash
# Test in canary namespace first
kubectl apply -f deployment.yaml -n canary

# If working, apply to production
kubectl apply -f deployment.yaml -n production
```

## Escalation Path
1. **Initial failure**: Check logs, attempt rollback if safe
2. **Rollback successful**: Post-mortem, fix root cause
3. **Rollback fails**: Page infrastructure team, activate incident commander
4. **Multiple deployments failing**: Escalate to architecture team

## Prevention
- Test deployment in staging environment first
- Use canary deployments for gradual rollout
- Monitor error rates and latency during deployment
- Have health checks that accurately represent service readiness
- Run load tests before production deployment
- Keep deployment tooling up to date
