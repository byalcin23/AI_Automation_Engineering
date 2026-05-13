# High CPU Usage Runbook

## Problem Statement
High CPU usage indicates that compute resources are exhausted or being consumed by inefficient processes. This can cause application slowness, timeouts, and cascading failures.

## Severity Levels
- **Critical**: CPU > 90% sustained
- **High**: CPU 70-90%
- **Medium**: CPU 50-70%
- **Low**: CPU < 50%

## Immediate Actions
1. Get current process list: `ps aux --sort=-%cpu | head -20`
2. Check system load: `uptime` or `top`
3. Identify the top CPU consumer
4. Check if it's expected (e.g., deployment, backup)
5. Assess impact on user-facing services

## Diagnosis Steps
1. **Identify the culprit process**:
   ```bash
   top -b -o %CPU | head -15
   ps -eo pid,user,%cpu,comm | sort -k3 -rn | head -10
   ```

2. **Check application logs**: Look for errors or warnings
3. **Check for recent deployments**: `git log --oneline -5`
4. **Check container stats**: If running in Kubernetes
   ```bash
   kubectl top nodes
   kubectl top pods
   ```

5. **Monitor CPU per thread**:
   ```bash
   ps -mp <PID> -o THREAD,tid,time
   ```

## Common Causes and Solutions

### Memory Leak in Application
- **Symptom**: Memory usage grows steadily, CPU spikes follow
- **Fix**: Restart application, deploy fix for memory leak
- **Check**: Monitor memory trends: `free -h` every minute for 10 minutes

### Runaway Query or Job
- **Symptom**: Database process consuming CPU, queries slow
- **Fix**: Kill long-running query, optimize, add indexes
- **Command**: `KILL QUERY <PROCESS_ID>;` or `pkill -f pattern`

### Recent Deployment Issue
- **Symptom**: CPU spike after deployment
- **Fix**: Rollback to previous version or debug new code
- **Verify**: Check deployment logs and code changes

### Misconfigured Process
- **Symptom**: Unexpected process running or respawning
- **Fix**: Review configuration, adjust process limits
- **Check**: `crontab -l`, `systemctl list-timers`

### Resource Contention
- **Symptom**: CPU usage high across all processes
- **Fix**: Scale horizontally, upgrade resources
- **Plan**: Implement auto-scaling policies

## Emergency Response
1. **If critical impact**: Trigger page-all, focus on stabilization
2. **Restart affected service**: `systemctl restart service-name`
3. **Drain traffic**: Remove from load balancer if needed
4. **Scale up**: Add more instances if using orchestration
5. **Communicate**: Update status page

## Escalation Path
- **70-85% CPU**: Monitor closely, alert team
- **85-95% CPU**: Page on-call, start remediation
- **> 95% CPU**: Immediate escalation, consider failover
- **Service impact**: Activate incident commander

## Prevention
- Set CPU limits in containers/processes
- Regular performance testing and optimization
- Monitor trend over time, alert on increases
- Load testing before major releases
