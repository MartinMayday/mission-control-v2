# Roadmap for Option A: Start Implementation Now

## Phase 1: Docker Foundation (Weeks 1-2)

### Task 1.1: Prerequisites Verification
- **Scope:** Verify OrbStack, Docker, and SSH key readiness
- **Files:** `~/.ssh/id_ed25519_coder`, Docker outputs
- **Dependencies:** None
- **Verification:**
  - `orb list` returns success
  - `docker --version` shows 20.10+
  - `ls -la ~/.ssh/id_ed25519_coder` exists
- **Estimated context:** 32K

### Task 1.2: Create Project Structure
- **Scope:** Create directory layout and Git repository
- **Files:** `~/openclaw-deployment/`, `.gitignore`, `README.md`
- **Dependencies:** Task 1.1
- **Verification:**
  - All directories created
  - Git repository initialized
  - `.gitignore` excludes `.env`, secrets
- **Estimated context:** 64K

### Task 1.3: Deploy Docker Compose Stack
- **Scope:** Deploy observability stack (Prometheus, Loki, Tempo, Grafana, PostgreSQL, MinIO)
- **Files:** `~/openclaw-deployment/docker-compose.yml`, `.env`
- **Dependencies:** Task 1.2
- **Verification:**
  - `docker compose ps` shows all services running
  - `curl http://localhost:3000` returns Grafana UI
  - Prometheus metrics endpoint accessible
- **Estimated context:** 128K

### Task 1.4: Configure OpenTelemetry Collector
- **Scope:** Setup OTEL collector for unified telemetry pipeline
- **Files:** `~/openclaw-deployment/otel-collector-config.yaml`
- **Dependencies:** Task 1.3
- **Verification:**
  - OTEL collector running without errors
  - Metrics flowing to Prometheus
  - Logs flowing to Loki
  - Traces flowing to Tempo
- **Estimated context:** 128K

### Task 1.5: Deploy Webhook Receiver
- **Scope:** Create webhook service for OpenClaw deployment events
- **Files:** `~/openclaw-deployment/webhook-receiver/` (Python/FastAPI app)
- **Dependencies:** Task 1.3
- **Verification:**
  - Webhook endpoint responds to POST
  - Events stored in PostgreSQL
  - OTEL headers injected correctly
- **Estimated context:** 128K

### Task 1.6: Implement Conversation ID Generator
- **Scope:** UUID v7 generator with timestamp extraction
- **Files:** `~/openclaw-deployment/webhook-receiver/conversation.py`
- **Dependencies:** Task 1.5
- **Verification:**
  - UUID v7 format validated
  - Timestamp extraction accurate
  - Collision resistance tested (1M generations)
- **Estimated context:** 64K

### Task 1.7: Configure Grafana Dashboards
- **Scope:** Import pre-built dashboards for unified observability
- **Files:** `~/openclaw-deployment/grafana/dashboards/` (JSON files)
- **Dependencies:** Task 1.3, Task 1.4
- **Verification:**
  - All dashboards imported successfully
  - Data sources connected
  - Sample queries return results
- **Estimated context:** 128K

---

## Phase 2: Production Hardening (Weeks 3-4)

### Task 2.1: Setup GitOps Repository
- **Scope:** Create Git repo for declarative infrastructure
- **Files:** `~/openclaw-infra/`, ArgoCD Application manifests
- **Dependencies:** Phase 1 complete
- **Verification:**
  - Git repository initialized
  - ArgoCD manifests created
  - First deployment committed
- **Estimated context:** 64K

### Task 2.2: Deploy ArgoCD
- **Scope:** Install ArgoCD for GitOps synchronization
- **Files:** `~/openclaw-deployment/argocd/`
- **Dependencies:** Task 2.1
- **Verification:**
  - ArgoCD UI accessible at localhost:8080
  - Cluster synced successfully
  - Auto-sync enabled
- **Estimated context:** 128K

### Task 2.3: Configure External Secrets Operator
- **Scope:** Setup secret management without storing in Git
- **Files:** `~/openclaw-deployment/external-secrets/`
- **Dependencies:** Task 2.2
- **Verification:**
  - Secrets loaded from environment variables
  - No secrets in Git repository
  - Secret rotation works (test rotation)
- **Estimated context:** 128K

### Task 2.4: Implement Conversation Correlation Engine
- **Scope:** Build service linking conversation_id → Git SHA → deployments
- **Files:** `~/openclaw-deployment/correlation-engine/`
- **Dependencies:** Task 1.6, Task 2.2
- **Verification:**
  - Git commits tagged with conversation_id
  - Deployment events linked to Git SHA
  - End-to-end trace queryable in Grafana
- **Estimated context:** 128K

### Task 2.5: Deploy OPA Gatekeeper
- **Scope:** Setup policy enforcement for deployments
- **Files:** `~/openclaw-deployment/gatekeeper/policies.yaml`
- **Dependencies:** Task 2.2
- **Verification:**
  - Gatekeeper pods running
  - Sample policy enforced
  - Violation blocks deployment
- **Estimated context:** 128K

### Task 2.6: Configure Velero for Backups
- **Scope:** Setup Kubernetes snapshots for disaster recovery
- **Files:** `~/openclaw-deployment/velero/`
- **Dependencies:** Task 2.2
- **Verification:**
  - Velero installed and configured
  - Manual backup succeeds
  - Backup verification passes
- **Estimated context:** 128K

### Task 2.7: Setup Automated Backup Schedule
- **Scope:** Configure cron schedule for 6-hourly backups with 90-day retention
- **Files:** `~/openclaw-deployment/backup/schedule.yaml`
- **Dependencies:** Task 2.6
- **Verification:**
  - Cron schedule active (every 6 hours)
  - Backup triggers automatically
  - Oldest backups pruned after 90 days
- **Estimated context:** 64K

### Task 2.8: Implement Rollback Mechanisms
- **Scope:** Build rollback CLI tools (by conversation, time, Git SHA)
- **Files:** `~/openclaw-deployment/rollback/` (CLI scripts)
- **Dependencies:** Task 2.4, Task 2.6
- **Verification:**
  - Rollback by conversation_id works
  - Rollback by timestamp works
  - Rollback by Git SHA works
  - Rollback completes in <5 minutes
- **Estimated context:** 128K

---

## Phase 3: VM Migration (Weeks 5-6)

### Task 3.1: Create OrbStack VM
- **Scope:** Provision Ubuntu 22.04 VM with allocated resources
- **Files:** VM configuration
- **Dependencies:** Phase 2 complete
- **Verification:**
  - VM running with 2 vCPU, 4GB RAM, 20GB disk
  - SSH accessible on port 717
  - `~/.ssh/id_ed25519_coder` authentication works
- **Estimated context:** 64K

### Task 3.2: Harden VM Security
- **Scope:** Apply baseline hardening (fail2ban, ufw, automatic updates)
- **Files:** `/etc/ssh/sshd_config`, `/etc/fail2ban/jail.local`
- **Dependencies:** Task 3.1
- **Verification:**
  - fail2ban running and blocking IPs
  - ufw allows only necessary ports
  - Unattended upgrades enabled
  - SSH hardening applied (key-only, no root)
- **Estimated context:** 128K

### Task 3.3: Migrate Docker Compose to VM
- **Scope:** Transfer all containers and configurations to VM
- **Files:** Copy `~/openclaw-deployment/` to VM
- **Dependencies:** Task 3.2
- **Verification:**
  - All services running on VM
  - Metrics/logs/traces flowing from VM
  - Data migration complete (MinIO, PostgreSQL)
- **Estimated context:** 128K

### Task 3.4: Configure VM Firewall Rules
- **Scope:** Setup ufw rules blocking port 18789 from internet
- **Files:** `/etc/ufw/rules.v4`
- **Dependencies:** Task 3.3
- **Verification:**
  - Port 18789 bound to localhost only
  - `sudo ss -tlnp` confirms no 0.0.0.0:18789
  - External scan shows port closed
- **Estimated context:** 64K

### Task 3.5: Test VM Rollback Capability
- **Scope:** Verify rollback works in VM environment
- **Files:** Rollback scripts tested on VM
- **Dependencies:** Task 3.4
- **Verification:**
  - Rollback by conversation_id works on VM
  - VM snapshots usable for restore
  - RTO <1 hour verified
- **Estimated context:** 128K

---

## Phase 4: Learning System (Weeks 7-8)

### Task 4.1: Deploy Qdrant Vector Database
- **Scope:** Setup Qdrant for pattern storage and similarity search
- **Files:** `docker-compose.yml` (add Qdrant service)
- **Dependencies:** Phase 3 complete
- **Verification:**
  - Qdrant accessible at localhost:6333
  - Collections created successfully
  - Vector insertion works
- **Estimated context:** 64K

### Task 4.2: Build Pattern Extraction Pipeline
- **Scope:** Create service analyzing deployment logs for patterns
- **Files:** `~/openclaw-deployment/pattern-extractor/`
- **Dependencies:** Task 4.1
- **Verification:**
  - Logs parsed successfully
  - Patterns extracted and stored
  - Embeddings generated for similarity search
- **Estimated context:** 128K

### Task 4.3: Implement Similarity Search
- **Scope:** Build API for situation matching based on historical patterns
- **Files:** `~/openclaw-deployment/similarity-search/`
- **Dependencies:** Task 4.2
- **Verification:**
  - Vector search returns relevant patterns
  - Search ranked by similarity score
  - Response time <500ms for 90% queries
- **Estimated context:** 128K

### Task 4.4: Create Recommendation Engine
- **Scope:** Build service providing actionable recommendations
- **Files:** `~/openclaw-deployment/recommendation-engine/`
- **Dependencies:** Task 4.3
- **Verification:**
  - Recommendations generated from patterns
  - Recommendations displayed in Grafana
  - User feedback loop captures effectiveness
- **Estimated context:** 128K

### Task 4.5: Integrate Learning Dashboard
- **Scope:** Add learning panel to Grafana showing insights
- **Files:** `~/openclaw-deployment/grafana/dashboards/learning.json`
- **Dependencies:** Task 4.4
- **Verification:**
  - Learning dashboard displays patterns
  - Recommendations actionable
  - Historical trends visible
- **Estimated context:** 64K

### Task 4.6: End-to-End Testing
- **Scope:** Complete system testing with rollback scenarios
- **Files:** Test scripts in `~/openclaw-deployment/tests/`
- **Dependencies:** All previous tasks
- **Verification:**
  - All acceptance criteria met
  - Rollback tested and verified
  - Backup/restore tested
  - Learning system extracting patterns
  - Cost monitoring active
- **Estimated context:** 128K

---

## Context Budget Summary

| Phase | 32K Tasks | 64K Tasks | 128K Tasks | Total Tasks |
|-------|-----------|-----------|------------|-------------|
| Phase 1 | 1 | 2 | 4 | 7 |
| Phase 2 | 0 | 2 | 6 | 8 |
| Phase 3 | 0 | 2 | 3 | 5 |
| Phase 4 | 0 | 2 | 4 | 6 |
| **Total** | **1** | **8** | **17** | **26** |

**Total Estimated Context Tokens:** 2,432K (2.4M tokens across all tasks)

**Note:** Each task executes in fresh 200K context via Task tool (subagent), preventing context rot and ensuring consistent quality.

---

## Execution Order

Tasks execute sequentially within phases, but independent tasks within same phase can run in parallel:

**Phase 1 Parallelization:**
- Stream A: 1.1 → 1.2 → 1.3 → 1.4 → 1.7 (Core infrastructure)
- Stream B: 1.5 → 1.6 (Webhook system, depends on 1.3)

**Phase 2 Parallelization:**
- Stream A: 2.1 → 2.2 → 2.3 → 2.5 (GitOps core)
- Stream B: 2.4 → 2.8 (Correlation + rollback, depends on Stream A)
- Stream C: 2.6 → 2.7 (Backup system, independent)

**Phase 3:** Sequential (VM migration requires step-by-step)

**Phase 4 Parallelization:**
- Stream A: 4.1 → 4.2 → 4.3 → 4.4 → 4.5
- Stream B: 4.6 (Testing, depends on Stream A complete)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Context degradation** | Fresh context per task (Task tool) |
| **Integration failures** | Verification gates between phases |
| **Cost overrun** | Grafana cost monitoring dashboard |
| **Backup failure** | Verification after each backup |
| **VM migration issues** | Docker fallback always available |

---

## Success Metrics

- All 26 tasks completed with verification passing
- Grafana dashboard loads in <3 seconds
- Rollback completes in <5 minutes
- Backup success rate >99%
- 90-day data retention confirmed
- Cost monitoring shows <$10/month
- Learning system extracting patterns from day 1

---

*Generated via GSD Workflow | Spec-Driven Development with Context Freshness*
*Option A: Start Implementation Now | Total Timeline: 8 weeks*
