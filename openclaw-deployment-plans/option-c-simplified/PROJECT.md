# Option C: Simplified Approach (Velero + Restic Only)

## Vision

Deploy essential backup and rollback infrastructure using Velero and Restic, providing time-machine recovery capability without the complexity of full observability and learning systems.

## Problem Statement

Martin needs deployment tracking and rollback capability, but the full observability stack may be overkill for current needs. This option provides:
- Core backup and disaster recovery
- Time-machine rollback capability
- File-level and container-level snapshots
- Set-and-forget automation
- Minimal complexity and maintenance

**Why Option C?**
- Focus on essential capability: rollback and backup
- Avoid observability complexity (Prometheus/Loki/Tempo/Grafana)
- Skip GitOps learning curve (ArgoCD, conversation correlation)
- No learning system overhead (Qdrant, pattern extraction)
- Faster time to value with lower complexity

## Success Criteria

- [ ] Velero installed and configured for Docker volume backups
- [ ] Restic configured for file-level backups
- [ ] Automated backup schedule running every 6 hours
- [ ] Backup verification after each backup
- [ ] Rollback tested and working (<5 minutes)
- [ ] 90-day retention with automated pruning
- [ ] Disaster recovery tested (RTO <1 hour)

## Constraints

- **Complexity:** 2/5 (significantly simpler than Options A/B)
- **Timeline:** 4 weeks (vs 8 weeks for Option A)
- **Budget:** $2/month self-hosted (vs $6/month for full stack)
- **Resources:** 2 vCPU, 4GB RAM, 100GB disk (vs 11.5 vCPU, 22GB RAM, 665GB disk)
- **Scope:** Backup and rollback only
- **Security:** Same zero-trust infrastructure (Velero supports encryption)

## Out of Scope

- Observability stack (Prometheus, Loki, Tempo, Grafana, Pyroscope)
- GitOps automation (ArgoCD, External Secrets, OPA Gatekeeper)
- Conversation ID correlation (no PostgreSQL tracking)
- Learning system (Qdrant, pattern extraction, recommendations)
- Unified dashboards
- Cost monitoring (minimal resource usage makes this unnecessary)

## Dependencies

- OrbStack and Docker operational
- OpenClaw deployed (or ready to deploy)
- S3-compatible storage (MinIO or Backblaze B2)
- Basic Docker knowledge for volume management

## Key Differences from Option A

| Aspect | Option A (Full Stack) | Option C (Simplified) |
|--------|----------------------|-----------------------|
| **Timeline** | 8 weeks | 4 weeks |
| **Complexity** | 3/5 | 2/5 |
| **Components** | 15+ services | 2 services (Velero, Restic) |
| **Resource Usage** | 11.5 vCPU, 22GB RAM, 665GB disk | 2 vCPU, 4GB RAM, 100GB disk |
| **Cost** | $6/month | $2/month |
| **Capabilities** | Full observability + GitOps + learning | Backup + rollback only |
| **Conversation Tracking** | Yes (PostgreSQL + UUID correlation) | No (timestamp-based only) |
| **Dashboards** | Yes (Grafana) | No (CLI only) |
| **Learning System** | Yes (Qdrant + pattern extraction) | No |

## Trade-offs

**What You Gain:**
- Faster deployment (4 weeks vs 8 weeks)
- Lower complexity (2/5 vs 3/5)
- Lower cost ($2/month vs $6/month)
- Lower resource usage (83% reduction)
- Easier maintenance
- Fewer integration points
- Lower risk

**What You Lose:**
- No unified observability (metrics/logs/traces)
- No GitOps automation (manual commits)
- No conversation-to-deployment correlation
- No learning system
- No Grafana dashboards
- Manual rollback (no conversation ID queries)
- No pattern extraction
- No recommendations

## When to Choose Option C

**Choose Option C if:**
- Primary need is backup and rollback capability
- Observability is "nice to have" not "must have"
- Want to validate approach before investing in full stack
- Prefer simplicity over comprehensive tracking
- Timeline is constrained (need faster delivery)
- Resource budget is limited

**Don't Choose Option C if:**
- You need detailed metrics and logs
- You want conversation-level correlation
- You plan to extract learnings from deployment patterns
- You value automation over manual processes
- You need visual dashboards

## Upgrade Path

Option C can be upgraded to Option A later if needs evolve:

**Phase 1:** Start with Option C (4 weeks)
**Phase 2:** Add observability (Prometheus + Loki + Tempo + Grafana) → 4 weeks
**Phase 3:** Add GitOps (ArgoCD + conversation correlation) → 4 weeks
**Phase 4:** Add learning system (Qdrant + pattern extraction) → 4 weeks

**Total:** 16 weeks incremental vs 8 weeks big bang (but with validation at each step)

## Expected Outcomes

**Immediate Value (Week 1-4):**
- Automated backups running
- Rollback capability operational
- Disaster recovery validated

**Future-Proofing:**
- All backups compatible with full observability stack
- Velero snapshots migrate to Kubernetes if needed
- Restic repositories portable to any platform

**Risk Reduction:**
- Lower complexity = fewer failure modes
- Simpler stack = easier troubleshooting
- Faster deployment = earlier risk identification
