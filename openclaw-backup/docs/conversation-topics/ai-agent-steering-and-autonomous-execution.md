# AI Agent Steering and Autonomous Execution System

**Conversation Date:** 2026-02-04
**Topic ID:** AI_AGENT_STEERING_001
**Status:** Requirements Defined
**Related Projects:** Option C (Backup), Option A (Observability + Learning)

---

## Primary Title

**"AI Agent Steering and Autonomous Execution: From Manual Babysitting to Fire-and-Forget Orchestration"**

---

## Alternative Titles

1. **"CI/CD Pipelines for AI Agents: Architecture for Autonomous Execution"**
2. **"Agent Control Systems: Steering, Validation, and Learning in Production"**
3. **"Beyond GSD Workflow: External Orchestration for Background AI Execution"**
4. **"The Missing Layer: AI Agent Steering Controls for Production-Grade Execution"**
5. **"From Slash Commands to Autonomous Agents: Building the Execution Layer"**

---

## Core Problem Statement

**Current State:**
- AI/LLM agents execute without runtime steering
- No enforcement of plan adherence during execution
- No evidence grounding or fact-checking gates
- Unpredictable outcomes when agents "make things up"
- Manual babysitting required (slash command → wait → next command)
- Execution stops when Claude Code session ends

**Desired State:**
- Agents follow enforced plans with immutable context
- Runtime checkpoints validate progress
- Evidence requirements prevent hallucinations
- Fact-checking gates validate critical decisions
- Autonomous execution continues in background
- Notifications on completion with test results

---

## Key Themes Discussed

### 1. Agent Steering Architecture
**What:** Enforcement mechanisms for AI agent execution
**Components:**
- ExecutionContextTemplate (immutable facts injected per task)
- Checkpoint validation (verify on-track at token intervals)
- Evidence gates (require citations for technical claims)
- Fact-checking hooks (validate critical decisions)
- Red lines (stop conditions that prevent bad outcomes)

**Key Insight:** The problem isn't that agents are unpredictable - it's that we don't enforce constraints on their execution.

### 2. GSD Workflow Limitations
**What:** Clarification that GSD is a skill (not core PAI), based on external repo
**Issue:** Requires manual slash commands for each phase
**Gap:** No autonomous execution, no background persistence
**User Pain:** "I have to manually sit and wait for things to finish and run next related slash-command"

### 3. Autonomous AI Execution Vision
**What:** CI/CD pipeline for AI agents
**Flow:**
```
Plan Creation → Handoff → Background Execution → Monitoring → Notification
```
**Requirements:**
- External orchestration (survives Claude Code restarts)
- Progress monitoring with health checks
- Voice/push notifications on completion
- Testing/validation/evaluation automation
- Integration with observability stack

### 4. Option A Integration
**What:** Full observability + learning system enables autonomy
**Components:**
- PostgreSQL: Conversation tracking
- Qdrant: Vector DB for pattern storage
- Pattern extraction pipeline
- Recommendation engine
- Prometheus/Loki/Grafana: Observability

**Key Insight:** "The project we are going to deploy is fully autonomy and show promising results" = Option A's learning system

### 5. Orchestration Options
**Evaluated:**
- **Prefect (Recommended):** Python-based, low learning curve, 768MB RAM
- **Temporal:** Go-based, durable execution, more complex
- **Airflow:** Not recommended (overkill for this use case)
- **Custom TypeScript:** Viable for minimal footprint (~640MB RAM)

**Decision:** External orchestration (NOT within Claude Code)

---

## Decisions Made

### 1. Agent Steering Architecture Designed
**Status:** ✅ Complete
**Artifacts:**
- `~/.claude/skills/PAI/AGENT_STEERING_ARCHITECTURE.md`
- `~/.claude/templates/steering/phase2-velero-context.yaml`
- `~/.claude/templates/steering/README.md`
- Gate scripts: port-conflict, minio-connectivity, checkpoint-validate

**Key Features:**
- Immutable context templates per phase
- 6 checkpoints at 32K token intervals
- Evidence requirements for Velero Docker plugin research
- Red lines: reserved ports, no evidence = stop

### 2. Autonomous Execution Requirements Documented
**Status:** ✅ Complete
**Artifact:** `~/openclaw-backup/docs/autonomous-execution-requirements.md` (1,336 lines)

**Contents:**
- 6 user stories (handoff, persistence, monitoring, notifications, learning, testing)
- Technical requirements (execution system, Option A integration)
- Architecture options (Prefect recommended)
- 5-phase implementation roadmap

### 3. External Orchestration Chosen
**Decision:** Use external orchestrator (not Claude Code internal)
**Rationale:**
- Survives Claude Code restarts
- True background execution
- Process isolation
- State persistence

**Recommendation:** Prefect (lowest effort, integrates with Docker)

### 4. Option A as Enabler
**Clarification:** Option A = "full autonomy project"
**Why:** Learning system (Qdrant) enables pattern extraction and recommendations
**Integration:**
- Conversation tracking → Pattern storage → Similarity search → Recommendations

---

## Documents Created

| File | Purpose | Size |
|------|---------|------|
| `AGENT_STEERING_ARCHITECTURE.md` | Complete steering architecture | 20KB |
| `phase2-velero-context.yaml` | Immutable context for Phase 2 | 8.4KB |
| `steering/README.md` | Implementation guide | 6KB |
| `autonomous-execution-requirements.md` | Requirements for autonomous system | 41KB |
| `checkpoint-validate.sh` | Checkpoint validation script | - |
| `port-conflict-gate.sh` | Port validation gate | - |
| `minio-connectivity-gate.sh` | MinIO connectivity gate | - |

---

## Key Insights

### 1. The Gap is Enforcement, Not Capability
**Insight:** AI agents are capable, but we don't enforce constraints during execution.
**Solution:** Add steering layer with gates, checkpoints, and evidence requirements.

### 2. Manual vs Autonomous is an Orchestration Problem
**Insight:** GSD workflow = manual execution; what's needed = orchestration layer.
**Solution:** External orchestrator (Prefect) for background execution.

### 3. Learning Enables True Autonomy
**Insight:** Option A's learning system (Qdrant) is the key to autonomous improvement.
**Solution:** Extract patterns from executions → store in Qdrant → similarity search → recommendations.

### 4. CI/CD Pattern Applies to AI Agents
**Insight:** AI agent execution follows same pattern as software deployment.
**Solution:** Treat AI agents like code: plan → test → deploy → monitor → notify.

---

## Next Steps

### Option A: Deploy Autonomous Execution System (Recommended)
**Phase 1:** Deploy Prefect orchestrator
- Docker Compose setup
- ROADMAP.md parser
- Claude Code handoff command

**Phase 2:** Implement notifications
- Voice server integration (localhost:8888)
- Push notifications
- Progress summaries

**Phase 3:** Integrate learning system
- Qdrant pattern extraction
- Similarity search
- Recommendation engine

**Timeline:** 2-3 weeks for basic system, 8 weeks for full autonomy

### Option B: Continue Option C Manually
- Complete Phase 2 (Velero) with steering controls
- Add autonomy later
- Lower upfront complexity

### Option C: Prototype and Validate
- Build minimal orchestrator (TypeScript)
- Test on Phase 2 execution
- Iterate based on learnings

---

## Related Conversations

**Pre-requisite:**
- Option A vs B vs C analysis (deployment strategy decision)
- Agent steering concerns (unpredictable AI execution)

**Follow-up:**
- Prefect deployment and configuration
- Qdrant integration for pattern learning
- Testing/evaluation automation

---

## Technical Context

**Current Stack:**
- Claude Code with PAI Algorithm
- GSD workflow skill (manual execution)
- OrbStack (Docker/VM)
- Option C: MinIO (Phase 1 deployed)
- Option A: Planned (Prometheus, Loki, Tempo, Grafana, Qdrant, ArgoCD)

**Target Stack:**
- Add: Prefect orchestrator (background execution)
- Add: Agent steering controls (enforcement)
- Add: Qdrant learning system (pattern extraction)
- Add: Notification system (voice, push, summaries)

---

## Success Criteria

**Phase 1 (Steering):**
- ✅ Agent steering architecture designed
- ✅ Requirements documented
- ⏳ Gate scripts debugged and tested
- ⏳ Integrated with GSD workflow

**Phase 2 (Autonomous Execution):**
- ⏳ Prefect deployed and operational
- ⏳ Background execution working
- ⏳ Notifications functional
- ⏳ Testing automation in place

**Phase 3 (Learning Integration):**
- ⏳ Qdrant integrated
- ⏳ Pattern extraction pipeline
- ⏳ Recommendation engine
- ⏳ Autonomous decision-making

---

## Quotes

> "The issue for me is I have to manually sit and wait for things to finish and run next related slash-command. I had hoped the gsd-workflow skill made it possible for claude-code with PAI implemented to create plans → handoff for execution and get notification when assignment done testing, validating, evaluating."

> "Current AI/LLM have no agent-steering, no boilerplate context, no plan to follow and does not clear context before new tasks starts development and no predictable outcome if AI/LLM make up stuff on the way with no control."

> "The project we are going to deploy is fully autonomy and show promising results." (Referring to Option A)

---

## Metadata

**Complexity:** 4/5 (Multi-layer architecture)
**Effort:** 8 weeks for full autonomous system
**Risk:** Medium (new orchestration layer, learning system integration)
**Priority:** High (enables all future AI agent work)

**Dependencies:**
- Option A observability stack (PostgreSQL, Qdrant, Prometheus)
- Docker/OrbStack for containerization
- Claude Code with PAI Algorithm

**Blocks:**
- None (can proceed in parallel with Option C deployment)

---

**Document Status:** Complete
**Last Updated:** 2026-02-04
**Maintained By:** Martin (with Claude/PAI assistance)
