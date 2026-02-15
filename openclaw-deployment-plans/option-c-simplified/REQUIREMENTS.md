# Requirements for Option C: Simplified Approach

## User Stories

### Story 1: Essential Backup Automation
**As** Martin, I need automated backups of OpenClaw deployment
**So that** I can recover from disasters without manual intervention

#### Acceptance Criteria
- [ ] Given 6 hours pass, when backup triggers, then all Docker volumes are automatically captured
- [ ] Given backup completes, when verification runs, then backup integrity is confirmed
- [ ] Given storage fills, when retention expires, then oldest backups are pruned automatically
- [ ] Given backup schedule configured, when I check logs, then backups run every 6 hours consistently

### Story 2: Time-Machine Rollback
**As** Martin, I need to restore any previous state quickly
**So that** I can undo changes that cause problems

#### Acceptance Criteria
- [ ] Given a deployment fails, when I trigger rollback, then system restores to previous state in <5 minutes
- [ ] Given I need specific point in time, when I specify timestamp, then system restores to that backup
- [ ] Given I need to undo specific changes, when I select backup, then only affected volumes are restored
- [ ] Given rollback completes, when I verify, then all services are healthy and data intact

### Story 3: Disaster Recovery Validation
**As** Martin, I need to test disaster recovery before real disaster strikes
**So that** I can trust my backup system

#### Acceptance Criteria
- [ ] Given I simulate disaster, when I trigger restore, then complete system recovers with <1 hour RTO
- [ ] Given restore completes, when I verify, then all OpenClaw services function normally
- [ ] Given I test corruption scenario, when I restore from backup, then data integrity is confirmed
- [ ] Given disaster occurs, when I need to recover, then documented procedure works as tested

### Story 4: File-Level Recovery
**As** Martin, I need to restore individual files without full system rollback
**So that** I can fix mistakes without major disruption

#### Acceptance Criteria
- [ ] Given I accidentally delete a file, when I use Restic, then I can restore single file from backup
- [ ] Given I need previous version of config, when I query Restic, then I can restore specific file version
- [ ] Given I need to compare versions, when I list snapshots, then I can see all available backups
- [ ] Given file restore completes, when I verify, then file is intact and correct

### Story 5: Set-and-Forget Operation
**As** Martin, I need backup system that runs without daily attention
**So that** I can focus on development instead of maintenance

#### Acceptance Criteria
- [ ] Given system deployed, when I configure cron schedule, then backups run automatically every 6 hours
- [ ] Given backup runs, when it completes, then notification confirms success or alerts failure
- [ ] Given 90 days pass, when retention policy runs, then old backups are pruned without manual intervention
- [ ] Given I need backup status, when I query system, then I can see last backup time and next scheduled backup

## Technical Requirements

### Backup Infrastructure
- [ ] **Velero 1.14+** for Docker volume snapshots
  - Plugin for Docker volume storage
  - S3-compatible backend (MinIO or Backblaze B2)
  - Schedule definition for 6-hour intervals
  - Retention policy: 90 days
  - Backup verification hook
  - Restore timeout: 1 hour

- [ ] **Restic 0.17+** for file-level backups
  - Repository initialization
  - S3-compatible backend (same as Velero)
  - Daily snapshot schedule
  - Retention policy: 90 days
  - Automated pruning
  - Password protection

### Storage Backend
- [ ] **MinIO** (self-hosted) OR **Backblaze B2** (cloud)
  - S3-compatible API
  - Encryption at rest
  - Versioning enabled
  - Lifecycle rules for 90-day retention
  - Access control (credentials in environment variables)

### Automation
- [ ] **Cron jobs** for automated execution
  - Velero: `0 */6 * * *` (every 6 hours)
  - Restic: `0 2 * * *` (daily at 2 AM)
  - Restic prune: `0 3 * * 0` (weekly on Sunday)
  - Notification on completion (log + optional alert)

### Verification
- [ ] **Post-backup verification**
  - Velero: Backup describe command confirms success
  - Restic: Check command verifies repository integrity
  - Test restore to temporary location
  - Compare checksums
  - Alert on verification failure

### Rollback Tools
- [ ] **CLI scripts** for common operations
  - `rollback-latest.sh` - Restore most recent backup
  - `rollback-timestamp.sh` - Restore backup from specific time
  - `rollback-volume.sh` - Restore specific Docker volume
  - `restore-file.sh` - Restore single file from Restic
  - `list-backups.sh` - Show all available backups
  - `verify-backup.sh` - Verify backup integrity

### Documentation
- [ ] **Runbook** for disaster recovery
  - Step-by-step restore procedure
  - Common failure scenarios
  - Troubleshooting guide
  - Contact information (if external help needed)

## Non-Functional Requirements

### Performance
- [ ] Backup completes within 30-minute window
- [ ] Restore completes in <5 minutes for rollback
- [ ] Disaster recovery RTO <1 hour
- [ ] File-level restore <1 minute
- [ ] Verification adds <5 minutes to backup

### Scalability
- [ ] Handles 100GB of backup data (90-day retention)
- [ ] Supports incremental backups (only changed data)
- [ ] Concurrent backup operations don't interfere
- [ ] Storage growth is predictable and linear

### Reliability
- [ ] Backup success rate >99%
- [ ] Verification catches corruption before deletion
- [ ] Automated retry on transient failures
- [ ] Notifications sent on all failures
- [ ] Repository integrity check passes weekly

### Security
- [ ] All backups encrypted at rest (AES-256)
- [ ] Backup credentials stored in environment variables
- [ ] Transport encrypted (TLS for S3 API)
- [ ] Repository passwords never in git
- [ ] Access logging for all backup operations

### Maintainability
- [ ] Set-and-forget automation (no manual intervention for 30+ days)
- [ ] Automated pruning prevents storage exhaustion
- [ ] Clear logs for troubleshooting
- [ ] Simple CLI tools for manual operations
- [ ] Documentation covers all scenarios

### Usability
- [ ] One-command rollback to latest backup
- [ ] Clear backup listing with timestamps
- [ ] Simple restore commands for common scenarios
- [ ] Helpful error messages
- [ ] Progress indicators for long operations

### Cost
- [ ] Monthly cost target: $2/month (self-hosted MinIO)
- [ ] Optional: $6/TB/month for Backblaze B2
- [ ] Storage growth predictable (~1GB/day)
- [ ] 90-day retention = ~90GB storage
- [ ] Cost monitoring not required (minimal expense)

## Success Criteria Summary

**Option C Complete When:**
- [ ] All 5 user stories have acceptance criteria met
- [ ] Velero backups running every 6 hours
- [ ] Restic backups running daily
- [ ] Rollback tested and verified (<5 minutes)
- [ ] Disaster recovery validated (RTO <1 hour)
- [ ] File-level restore functional
- [ ] Set-and-forget operation confirmed (30+ days no intervention)
- [ ] Documentation complete and tested

**Key Metrics:**
- Backup success rate: >99%
- Rollback time: <5 minutes
- Disaster recovery RTO: <1 hour
- Storage usage: ~90GB for 90-day retention
- Monthly cost: $2 (self-hosted) or ~$0.50 (B2 for 90GB)
- Complexity: 2/5 (significantly simpler than Option A)

**Validation:**
- Run full disaster recovery test before considering complete
- Verify all rollback scenarios work
- Confirm 30 days of automated operation
- Document lessons learned
