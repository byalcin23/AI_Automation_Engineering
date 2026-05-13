# Database Stream Replication Lag Runbook

## Problem Statement
Stream replication lag occurs when the replica server falls behind the primary server in applying changes. This causes stale data reads and can indicate replication performance issues.

## Severity Levels
- **Critical**: Lag > 10 seconds
- **High**: Lag 5-10 seconds
- **Medium**: Lag 1-5 seconds
- **Low**: Lag < 1 second

## Immediate Actions
1. Check replication status: `SHOW SLAVE STATUS\G;`
2. Verify network connectivity between primary and replica
3. Check disk I/O on both servers: `iostat -x 1`
4. Monitor for query locks on primary: `SHOW PROCESSLIST;`

## Diagnosis Steps
1. **Check network latency**: Use `ping` or `mtr` between primary and replica
2. **Check query load on primary**: Look for long-running transactions
3. **Verify binary log position**: `SHOW MASTER STATUS;`
4. **Check replica thread status**: Look for Seconds_Behind_Master and Last_Error
5. **Monitor system resources**: CPU, memory, disk I/O on both servers

## Common Causes and Solutions

### High Query Load on Primary
- **Symptom**: replication lag increases during peak traffic
- **Fix**: Optimize slow queries, add indexes, scale read replicas
- **Command**: `SHOW SLOW LOG;` or check Percona Toolkit

### Network Issues
- **Symptom**: Lag spikes at regular intervals
- **Fix**: Check network bandwidth, latency between data centers
- **Command**: `iftop`, `nethogs`, network analysis tools

### Disk I/O Bottleneck
- **Symptom**: Lag worse on replica than primary
- **Fix**: Use SSD for binary logs, optimize InnoDB settings
- **Variable**: `innodb_flush_log_at_trx_commit=1` to `2` (trade-off)

### Replica Thread Crash
- **Symptom**: Seconds_Behind_Master shows NULL
- **Fix**: Check Last_Error, skip bad event if necessary
- **Command**: `SET GLOBAL SQL_SLAVE_SKIP_COUNTER=1; START SLAVE;`

## Escalation Path
1. **< 5s lag**: Monitor, no action needed
2. **5-30s lag**: Page on-call SRE, optimize queries
3. **> 30s lag**: Immediate escalation to database team, consider failover
4. **Complete failure**: Activate disaster recovery procedures

## Prevention
- Set up alerts for lag > 5 seconds
- Regular query optimization reviews
- Capacity planning for primary database
- Test failover procedures monthly
