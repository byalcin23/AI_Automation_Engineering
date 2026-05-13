# Disk Full Runbook

## Problem Statement
When disk space is exhausted, services become unable to write logs, temporary files, or data. This often causes cascading failures and rapid service degradation.

## Severity Levels
- **Critical**: Disk > 95% full, services failing to write
- **High**: Disk 85-95% full, risk of imminent failure
- **Medium**: Disk 70-85% full, warning threshold
- **Low**: Disk 50-70% full, normal operating range

## Immediate Actions
1. Check disk usage: `df -h` (view all filesystems)
2. Find the full filesystem: `df -h | grep -E '9[0-9]%|100%'`
3. Identify largest directories: `du -sh /* | sort -rh | head -10`
4. Stop new writes if critical: May need to stop logging temporarily
5. Assess service impact: Can services write? Are logs being dropped?

## Diagnosis Steps
1. **Identify full mount point**:
   ```bash
   df -h
   lsblk
   ```

2. **Find large files/directories**:
   ```bash
   du -sh /* | sort -rh
   find / -type f -size +100M -exec ls -lh {} \;
   ```

3. **Find hidden large files**:
   ```bash
   du -sh /path/to/mount/point/.*
   ls -lah /var/log/
   ```

4. **Check inodes** (sometimes issue is too many files, not size):
   ```bash
   df -i
   find / -iname "*.tmp" -o -iname "*.log" | wc -l
   ```

5. **Identify culprit service**:
   ```bash
   lsof +L1  # Shows deleted files still held open
   du -h --max-depth=1 /var/log/ | sort -rh
   ```

## Common Causes and Solutions

### Log Files Filling Disk
- **Symptom**: /var/log consuming 50-90% of space
- **Fix**: Archive old logs, enable log rotation
- **Check**: `du -sh /var/log/*`
- **Immediate**: `gzip /var/log/*.1` to compress
- **Permanent**: Configure logrotate, set retention policy

### Database Temp Files
- **Symptom**: /tmp or database directory full
- **Fix**: Clean temp directory, optimize database
- **Check**: `du -sh /tmp/`, `du -sh /var/lib/mysql/`
- **Immediate**: `rm -rf /tmp/*` (if safe), restart database
- **Permanent**: Configure temp directory cleanup, increase storage

### Unused Container Images or Build Artifacts
- **Symptom**: Docker images or build artifacts consuming space
- **Fix**: Clean up Docker, remove old images
- **Check**: `docker system df`, `docker images`
- **Immediate**: `docker system prune -a` (carefully!)

### Application Crash Dumps
- **Symptom**: Large core dump files in /var/crash
- **Fix**: Delete crash dumps, configure limits
- **Check**: `ls -lh /var/crash/`
- **Immediate**: `rm /var/crash/*`

### Temporary Files Not Cleaned
- **Symptom**: /tmp or /var/tmp full of orphaned files
- **Fix**: Clean temporary files, configure cleanup jobs
- **Check**: `find /tmp -type f -atime +7` (files not accessed in 7 days)
- **Immediate**: `rm -rf /tmp/*` (if no critical processes)

## Emergency Procedures

### When Disk is 98%+ Full
1. **Immediate**: Stop non-critical services to prevent writes
2. **Find and delete**: Identify and remove largest non-essential files
3. **Compress**: Gzip old log files: `gzip /var/log/*.1`
4. **Archive**: Move old files to external storage if available
5. **Restart**: Services may need restart after freeing space

### Quick Space Recovery
```bash
# Clean package manager cache
apt-get clean
yum clean all

# Clean temporary files
rm -rf /tmp/*
rm -rf /var/tmp/*

# Compress old logs
find /var/log -name "*.1" -type f -exec gzip {} \;

# Remove old Docker images
docker system prune -a

# Remove core dumps
rm -f /var/crash/*
```

## Long-term Solutions
1. **Monitor disk trends**: Alert when reaching 75%, 85%, 95%
2. **Implement log rotation**: Configure logrotate for all services
3. **Add storage**: Upgrade disk capacity or add additional drives
4. **Implement retention policies**: Archive old data, clean temp files
5. **Set up alerting**: Automated notifications before disk fills
6. **Regular reviews**: Weekly check of disk usage trends

## Escalation Path
- **70-80% full**: Monitor, plan storage expansion
- **80-90% full**: Alert team, start cleanup procedures
- **90-95% full**: Page on-call, immediate action required
- **95%+ full**: Critical escalation, may activate incident commander
- **Services impacted**: Full incident escalation

## Prevention
- Monitor disk usage trends, not just current state
- Set up automated alerts at 75%, 85%, 95%
- Implement automated cleanup jobs (cron)
- Regular storage capacity planning
- Archive historical data to separate storage
