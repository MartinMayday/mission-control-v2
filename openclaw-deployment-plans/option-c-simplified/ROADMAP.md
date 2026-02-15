# Roadmap for Option C: Simplified Approach

## Phase 1: Foundation Setup (Week 1)

### Task 1.1: Verify Prerequisites
- **Scope:** Confirm OrbStack, Docker, and OpenClaw readiness
- **Files:** Docker outputs, OpenClaw installation
- **Dependencies:** None
- **Verification:**
  - `orb list` returns success
  - `docker --version` shows 20.10+
  - OpenClaw running or ready to deploy
  - At least 100GB disk space available
- **Estimated context:** 32K

### Task 1.2: Create Project Directory Structure
- **Scope:** Setup directories for backup configuration and scripts
- **Files:** `~/openclaw-backup/`, `.gitignore`, `README.md`
- **Dependencies:** Task 1.1
- **Verification:**
  - Directory structure created
  - `.gitignore` excludes `.env` and credentials
  - README.md with overview
- **Estimated context:** 32K

### Task 1.3: Deploy MinIO for S3-Compatible Storage
- **Scope:** Setup self-hosted object storage for backups
- **Files:** `~/openclaw-backup/minio/docker-compose.yml`, `.env`
- **Dependencies:** Task 1.2
- **Verification:**
  - MinIO container running
  - Accessible at localhost:9000
  - Console accessible at localhost:9001
  - Bucket created for backups
  - Credentials stored in `.env`
- **Estimated context:** 64K

### Task 1.4: Configure Environment Variables
- **Scope:** Setup secure environment configuration
- **Files:** `~/openclaw-backup/.env`
- **Dependencies:** Task 1.3
- **Verification:**
  - MinIO credentials set
  - AWS-style S3 endpoint configured
  - Backup repository passwords generated
  - `.env` excluded from git (verify in `.gitignore`)
- **Estimated context:** 32K

---

## Phase 2: Velero Setup (Week 2)

### Task 2.1: Install Velero CLI
- **Scope:** Download and install Velero command-line tool
- **Files:** `/usr/local/bin/velero`
- **Dependencies:** Task 1.4
- **Verification:**
  - `velero version` returns 1.14+
  - CLI accessible from any directory
  - Autocompletion working (optional)
- **Estimated context:** 32K

### Task 2.2: Deploy Velero Server
- **Scope:** Deploy Velero server container with Docker plugin
- **Files:** `~/openclaw-backup/velero/docker-compose.yml`
- **Dependencies:** Task 2.1
- **Verification:**
  - Velero server container running
  - Docker volume plugin installed
  - `velero client config` shows correct S3 endpoint
  - `velero backup-location get` shows MinIO configured
- **Estimated context:** 64K

### Task 2.3: Configure Velero Backup Schedule
- **Scope:** Create cron schedule for 6-hourly backups
- **Files:** `~/openclaw-backup/velero/schedule.yaml`
- **Dependencies:** Task 2.2
- **Verification:**
  - Schedule created: `0 */6 * * *`
  - Next scheduled backup displayed
  - Schedule shows "Paused: false"
  - Associated Docker volumes listed
- **Estimated context:** 64K

### Task 2.4: Configure Velero Retention Policy
- **Scope:** Setup 90-day retention with automated pruning
- **Files:** `~/openclaw-backup/velero/retention.yaml`
- **Dependencies:** Task 2.3
- **Verification:**
  - Retention set to 2160 hours (90 days)
  - TTL configured for automatic deletion
  - Prune schedule configured (weekly)
- **Estimated context:** 32K

### Task 2.5: Create Velero Backup Verification Hook
- **Scope:** Add post-backup verification to ensure integrity
- **Files:** `~/openclaw-backup/velero/verify-hook.sh`
- **Dependencies:** Task 2.4
- **Verification:**
  - Hook script executable
  - Runs after each backup
  - Logs verification results
  - Fails backup if verification fails
- **Estimated context:** 64K

### Task 2.6: Test Manual Velero Backup
- **Scope:** Run first manual backup to verify configuration
- **Files:** Test backup logs
- **Dependencies:** Task 2.5
- **Verification:**
  - Manual backup completes successfully
  - Backup appears in `velero backup get`
  - Backup status shows "Completed"
  - Backup size reasonable
  - Verification hook passes
- **Estimated context:** 64K

---

## Phase 3: Restic Setup (Week 3)

### Task 3.1: Install Restic CLI
- **Scope:** Download and install Restic command-line tool
- **Files:** `/usr/local/bin/restic`
- **Dependencies:** Task 2.6
- **Verification:**
  - `restic version` returns 0.17+
  - CLI accessible from any directory
- **Estimated context:** 32K

### Task 3.2: Initialize Restic Repository
- **Scope:** Create Restic repository in MinIO
- **Files:** `~/openclaw-backup/restic/repo-config`
- **Dependencies:** Task 3.1
- **Verification:**
  - `restic init` completes successfully
  - Repository password stored securely
  - `restic snapshots` shows empty repository
  - Repository accessible via S3 API
- **Estimated context:** 64K

### Task 3.3: Create Restic Backup Script
- **Scope:** Build script to backup OpenClaw configuration and data
- **Files:** `~/openclaw-backup/restic/backup.sh`
- **Dependencies:** Task 3.2
- **Verification:**
  - Script backs up all required directories
  - Script creates snapshot with descriptive tag
  - Script logs backup statistics
  - Manual test backup successful
- **Estimated context:** 64K

### Task 3.4: Configure Restic Schedule
- **Scope:** Setup cron job for daily Restic backups
- **Files:** `~/etc/cron.d/restic-backup` or user crontab
- **Dependencies:** Task 3.3
- **Verification:**
  - Cron entry created: `0 2 * * *`
  - Script executable by cron
  - Logs directory created
  - First scheduled backup runs successfully
- **Estimated context:** 64K

### Task 3.5: Configure Restic Retention and Pruning
- **Scope:** Setup 90-day retention with weekly pruning
- **Files:** `~/openclaw-backup/restic/forget.sh`, `~/etc/cron.d/restic-prune`
- **Dependencies:** Task 3.4
- **Verification:**
  - Forget policy configured: `--keep-daily 7 --keep-weekly 13 --keep-monthly 3`
  - Prune schedule created: `0 3 * * 0` (weekly Sunday)
  - Test `restic forget --dry-run` shows correct snapshots to keep
  - Test prune completes successfully
- **Estimated context:** 64K

### Task 3.6: Create Restic Restore Tools
- **Scope:** Build CLI scripts for file-level recovery
- **Files:** `~/openclaw-backup/restic/restore-file.sh`, `~/openclaw-backup/restic/list-snapshots.sh`
- **Dependencies:** Task 3.5
- **Verification:**
  - `restore-file.sh` restores single file from snapshot
  - `list-snapshots.sh` shows all snapshots with timestamps
  - Scripts provide usage instructions
  - Test file restore successful
- **Estimated context:** 64K

---

## Phase 4: Rollback & Disaster Recovery (Week 4)

### Task 4.1: Create Rollback CLI Tools
- **Scope:** Build scripts for common rollback scenarios
- **Files:** `~/openclaw-backup/rollback/rollback-latest.sh`, `rollback-timestamp.sh`, `rollback-volume.sh`
- **Dependencies:** Task 3.6
- **Verification:**
  - `rollback-latest.sh` restores most recent Velero backup
  - `rollback-timestamp.sh` accepts timestamp argument
  - `rollback-volume.sh` restores specific volume
  - All scripts show progress and confirmation
- **Estimated context:** 64K

### Task 4.2: Test Rollback to Latest Backup
- **Scope:** Verify rollback works in <5 minutes
- **Files:** Test logs
- **Dependencies:** Task 4.1
- **Verification:**
  - Intentionally break OpenClaw configuration
  - Run `rollback-latest.sh`
  - Restore completes in <5 minutes
  - OpenClaw services healthy after restore
  - Data integrity confirmed
- **Estimated context:** 64K

### Task 4.3: Test Point-in-Time Recovery
- **Scope:** Verify timestamp-based rollback works
- **Files:** Test logs
- **Dependencies:** Task 4.2
- **Verification:**
  - List available backups with timestamps
  - Select specific timestamp from past
  - Restore completes successfully
  - System state matches timestamp
- **Estimated context:** 64K

### Task 4.4: Create Disaster Recovery Runbook
- **Scope:** Document complete disaster recovery procedure
- **Files:** `~/openclaw-backup/DISASTER_RECOVERY.md`
- **Dependencies:** Task 4.3
- **Verification:**
  - Step-by-step restore procedure documented
  - Common failure scenarios covered
  - Troubleshooting section included
  - Contact information included (if needed)
  - Runbook reviewed for clarity
- **Estimated context:** 64K

### Task 4.5: Perform Full Disaster Recovery Test
- **Scope:** Simulate complete disaster and validate recovery
- **Files:** Test logs, screenshots
- **Dependencies:** Task 4.4
- **Verification:**
  - Stop all OpenClaw containers
  - Delete all Docker volumes (simulate disaster)
  - Follow runbook procedure
  - Complete system restore completed
  - RTO <1 hour validated
  - All services functional after recovery
  - Data integrity verified
- **Estimated context:** 128K

### Task 4.6: Configure Backup Notifications
- **Scope:** Setup alerts for backup success/failure
- **Files:** `~/openclaw-backup/notify.sh`, crontab entries
- **Dependencies:** Task 4.5
- **Verification:**
  - Velero backup completion triggers notification
  - Restic backup completion triggers notification
  - Verification failures trigger alert
  - Notification method chosen (log file, email, or webhook)
  - Test notifications received
- **Estimated context:** 64K

### Task 4.7: Create Monitoring Dashboard (Optional)
- **Scope:** Simple status dashboard for backup health
- **Files:** `~/openclaw-backup/status.sh`, optionally basic HTML dashboard
- **Dependencies:** Task 4.6
- **Verification:**
  - `status.sh` shows last backup time
  - Next scheduled backup displayed
  - Backup success rate visible
  - Storage usage shown
  - Optional: Simple web dashboard accessible
- **Estimated context:** 64K

### Task 4.8: Final Documentation and Handoff
- **Scope:** Complete documentation and validate set-and-forget operation
- **Files:** `~/openclaw-backup/README.md`, `~/openclaw-backup/OPERATIONS.md`
- **Dependencies:** Task 4.7
- **Verification:**
  - README.md complete with quick start
  - OPERATIONS.md covers all procedures
  - All scripts have usage instructions
  - 30-day set-and-forget test initiated
  - Success criteria validated:
    - All 5 user stories met
    - Backup success rate >99%
    - Rollback <5 minutes confirmed
    - Disaster recovery RTO <1 hour confirmed
    - Cost <$2/month confirmed
- **Estimated context:** 64K

---

## Context Budget Summary

| Phase | 32K Tasks | 64K Tasks | 128K Tasks | Total Tasks |
|-------|-----------|-----------|------------|-------------|
| Phase 1 | 2 | 2 | 0 | 4 |
| Phase 2 | 1 | 5 | 0 | 6 |
| Phase 3 | 0 | 6 | 0 | 6 |
| Phase 4 | 0 | 7 | 1 | 8 |
| **Total** | **3** | **20** | **1** | **24** |

**Total Estimated Context Tokens:** 1,400K (1.4M tokens across all tasks)

---

## Execution Order

All phases are sequential, but tasks within phases can have parallelization:

**Phase 1 (Foundation):** Sequential
- 1.1 → 1.2 → 1.3 → 1.4

**Phase 2 (Velero):** Sequential (each task depends on previous)
- 2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6

**Phase 3 (Restic):** Mostly sequential
- 3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6

**Phase 4 (Rollback & DR):** Some parallelization possible
- Stream A: 4.1 → 4.2 → 4.3 (CLI tools and testing)
- Stream B: 4.4 → 4.5 (Documentation and DR test, depends on Stream A)
- Stream C: 4.6 → 4.7 (Notifications and monitoring, parallel with Stream B after 4.4)
- Final: 4.8 (Documentation and validation, depends on all streams)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **MinIO data loss** | MinIO can be replicated to B2 for offsite backup |
| **Backup corruption** | Verification hook catches corruption before deletion |
| **Restore failure** | Regular testing (Task 4.5) validates restore procedure |
| **Storage exhaustion** | Retention policy automatically prunes old backups |
| **Credential exposure** | All credentials in `.env`, excluded from git |
| **Cron failures** | Notifications alert on backup failures |

---

## Success Metrics

**Phase 1 Complete When:**
- MinIO deployed and accessible
- Environment configured securely
- Directory structure ready

**Phase 2 Complete When:**
- Velero installed and configured
- 6-hourly backup schedule running
- First manual backup successful
- Verification hook operational

**Phase 3 Complete When:**
- Restic installed and repository initialized
- Daily backups running
- Retention and pruning configured
- File restore tools working

**Phase 4 Complete When:**
- All rollback scenarios tested
- Disaster recovery validated (RTO <1 hour)
- Documentation complete
- 30-day set-and-forget operation initiated

**Overall Success Criteria:**
- [ ] All 5 user stories met
- [ ] Backup success rate >99%
- [ ] Rollback time <5 minutes
- [ ] Disaster recovery RTO <1 hour
- [ ] Storage usage ~90GB (predictable)
- [ ] Monthly cost <$2
- [ ] Complexity rating 2/5 confirmed
- [ ] 30 days automated operation successful

---

## Comparison to Option A

| Metric | Option C (Simplified) | Option A (Full) |
|--------|----------------------|-----------------|
| **Timeline** | 4 weeks | 8 weeks |
| **Tasks** | 24 tasks | 26 tasks |
| **Context Budget** | 1.4M tokens | 2.4M tokens |
| **Components** | 2 (Velero, Restic) | 15+ |
| **vCPU** | 2 | 11.5 |
| **RAM** | 4GB | 22GB |
| **Disk** | 100GB | 665GB |
| **Cost** | $2/month | $6/month |
| **Complexity** | 2/5 | 3/5 |

**Option C is 50% faster, uses 83% fewer resources, and costs 67% less.**

---

*Generated via GSD Workflow | Spec-Driven Development with Context Freshness*
*Option C: Simplified Approach | Total Timeline: 4 weeks*
