# Autonomous AI Execution System - Requirements Document

**Document Version:** 1.0
**Date:** 2026-02-04
**Author:** Architect Agent
**Status:** Requirements Definition

---

## Executive Summary

This document defines requirements for an autonomous AI execution system that enables Martin to:
1. Create execution plans in Claude Code
2. Hand off to external orchestration for background execution
3. Monitor progress with health checks and persistence
4. Receive notifications on completion (voice, alerts, summaries)
5. Integrate with Option A's learning system (Qdrant, pattern extraction)
6. Automate testing/validation/evaluation cycles

**Key Design Principle:** External orchestration (NOT within Claude Code) for true background execution that survives Claude Code restarts and session termination.

---

## Table of Contents

1. [User Stories](#user-stories)
2. [Autonomous Execution System Requirements](#autonomous-execution-system-requirements)
3. [Integration with Option A](#integration-with-option-a)
4. [External Orchestration Options](#external-orchestration-options)
5. [Testing/Validation Automation](#testingvalidation-automation)
6. [Architecture Options](#architecture-options)
7. [Success Criteria](#success-criteria)
8. [Implementation Roadmap](#implementation-roadmap)

---

## 1. User Stories

### Story 1: Plan-to-Execution Handoff

**As** Martin,
**I want** to create an execution plan in Claude Code and hand it off to an external orchestrator,
**So that** execution continues in the background even if I close Claude Code or my computer restarts.

#### Acceptance Criteria

- [ ] Given a valid plan file (ROADMAP.md, specs), when I invoke the handoff command, then the external orchestrator accepts the plan
- [ ] Given handoff initiated, when Claude Code closes, then execution continues unperturbed
- [ ] Given plan execution, when I check status, then I see current progress and remaining tasks
- [ ] Given plan completion, when execution finishes, then I receive notification with results summary

#### Input Formats Supported

| Input Type | Format | Validation |
|------------|--------|------------|
| **ROADMAP.md** | GSD format with atomic tasks | Parse tasks, dependencies, context tiers |
| **Spec files** | PRD/PRP with ISC criteria | Extract success criteria as verification gates |
| **Task list** | JSON/YAML task array | Load directly into execution queue |
| **Inline plan** | Markdown plan in conversation | Parse and extract before handoff |

---

### Story 2: Background Task Persistence

**As** Martin,
**I want** execution state to survive process restarts and system reboots,
**So that** long-running tasks complete reliably without manual intervention.

#### Acceptance Criteria

- [ ] Given task in progress, when orchestrator restarts, then task resumes from last checkpoint
- [ ] Given system reboot, when services recover, then orchestrator continues from persisted state
- [ ] Given task failure, when retry triggered, then state restored before execution attempt
- [ ] Given manual pause, when resumed, then execution continues from exact pause point

#### State Persistence Requirements

- Checkpoint every task boundary (before/after each atomic task)
- Store execution context (conversation ID, task ID, timestamp)
- Persist intermediate outputs (logs, artifacts, verification evidence)
- Support checkpoint rollback to any completed task

---

### Story 3: Progress Monitoring and Health Checks

**As** Martin,
**I want** real-time visibility into execution progress and system health,
**So that** I can detect issues early and take corrective action.

#### Acceptance Criteria

- [ ] Given execution in progress, when I query status, then I see current task, percent complete, ETA
- [ ] Given task failure, when health check runs, then I receive alert with error details
- [ ] Given long-running task, when timeout threshold approached, then I receive warning notification
- [ ] Given multiple parallel tasks, when I monitor, then I see individual task status across all streams

#### Health Check Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Task Duration** | >2x estimated | Warning notification |
| **Memory Usage** | >80% container limit | Alert, log dump |
| **Error Rate** | >3 consecutive failures | Halt execution, notify |
| **No Progress** | >10 min without log output | Warning, check for hang |
| **Disk Space** | <10% remaining | Alert, pause if critical |

---

### Story 4: Voice and Alert Notifications

**As** Martin,
**I want** to receive notifications on key events via voice and push alerts,
**So that** I stay informed without constantly checking status.

#### Acceptance Criteria

- [ ] Given task completes, when execution finishes, then voice notification announces completion
- [ ] Given error occurs, when task fails, then voice alert + push notification sent immediately
- [ ] Given phase transition, when major milestone reached, then voice update announces progress
- [ ] Given long execution, when >5 minutes elapsed, then periodic voice updates every 10 minutes

#### Notification Events

| Event | Voice | Push | Discord |
|-------|-------|------|---------|
| **Task Start** | Yes | No | No |
| **Task Complete** | Yes | Yes (if >5min) | No |
| **Task Failure** | Yes | Yes | Yes |
| **Phase Complete** | Yes | Yes | No |
| **Execution Complete** | Yes | Yes | Yes |
| **Health Warning** | Yes | Yes | No |

#### Voice Notification Format

Uses existing voice server at `localhost:8888`:

```bash
curl -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Execution task complete: deployed MinIO container successfully",
    "title": "Autonomous Execution",
    "voice_id": "{DAIDENTITY.VOICEID}"
  }'
```

---

### Story 5: Learning System Integration

**As** Martin,
**I want** the execution system to extract patterns and feed Option A's learning engine,
**So that** future executions benefit from historical knowledge.

#### Acceptance Criteria

- [ ] Given task completes, when execution succeeds, then conversation ID and outcome stored in PostgreSQL
- [ ] Given execution logs, when task finishes, then patterns extracted and embedded in Qdrant
- [ ] Given similar task requested, when I query, then recommendation engine suggests historical patterns
- [ ] Given failure occurs, when analysis runs, then failure patterns stored for future avoidance

#### Learning Pipeline

1. **Capture:** Store conversation ID, task spec, execution context
2. **Extract:** Parse logs for patterns (commands, errors, timing, outcomes)
3. **Embed:** Generate vector embeddings using existing embedding service
4. **Store:** Insert into Qdrant collection `execution_patterns`
5. **Retrieve:** On new task, query for similar historical executions
6. **Recommend:** Present top 3 similar past executions with outcomes

---

### Story 6: Automated Testing and Validation

**As** Martin,
**I want** execution to automatically run tests and verify outcomes,
**So that** I can trust results without manual inspection.

#### Acceptance Criteria

- [ ] Given task completes, when auto-test available, then test runner executes verification
- [ ] Given test failure, when validation fails, then execution halts with error report
- [ ] Given no auto-test, when task finishes, then manual verification checklist presented
- [ ] Given evaluation metrics, when task measurable, then scores recorded and trended

#### Validation Gates

| Gate Type | Trigger | Action on Fail |
|-----------|---------|----------------|
| **Pre-execution** | Before task starts | Halt, require manual approval |
| **Mid-execution** | At task checkpoint | Pause, alert, await decision |
| **Post-execution** | After task completes | Mark failed, skip dependents |
| **Evaluation** | After verification | Record score, continue if passing |

---

## 2. Autonomous Execution System Requirements

### 2.1 Input Acceptance

#### Plan File Parser

| Component | Function | Output |
|-----------|----------|--------|
| **ROADMAP.md Reader** | Parse GSD format tasks | Task list with dependencies |
| **Spec Extractor** | Parse PRD/PRP for ISC criteria | Verification criteria list |
| **Context Calculator** | Sum task context tiers | Total context budget |
| **Dependency Resolver** | Build task dependency graph | Execution order with parallelization |

#### Schema Definition

```typescript
interface ExecutionPlan {
  id: string;                    // UUID v7
  conversationId: string;        // Links to Claude Code conversation
  source: "ROADMAP" | "SPEC" | "TASK_LIST" | "INLINE";
  tasks: ExecutionTask[];
  metadata: {
    created: timestamp;
    estimatedDuration: number;   // minutes
    contextBudget: number;       // total tokens
    priority: "low" | "normal" | "high";
  };
}

interface ExecutionTask {
  id: string;                    // task-001, task-002, etc.
  title: string;                 // 8-word description
  description: string;           // Full task details
  dependencies: string[];        // Task IDs this depends on
  contextTier: 32 | 64 | 128 | 200;  // K tokens
  verification: VerificationCriterion[];
  status: "pending" | "in_progress" | "completed" | "failed" | "skipped";
  checkpoint?: CheckpointState;
}

interface VerificationCriterion {
  id: string;
  criterion: string;             // 8-word ISC criterion
  test: "auto" | "manual";
  result?: "pass" | "fail" | "skipped";
  evidence?: string;             // File path or output
}
```

---

### 2.2 Background Execution

#### Execution Engine Requirements

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **Process Isolation** | Each task in separate process/container | P0 |
| **Resource Limits** | CPU, memory, timeout per task | P0 |
| **Checkpoint/Resume** | State persistence at task boundaries | P0 |
| **Parallel Execution** | Independent tasks run concurrently | P1 |
| **Graceful Shutdown** | Complete current task on SIGTERM | P1 |
| **Retry Logic** | Configurable retry with exponential backoff | P1 |

#### Task Lifecycle

```
[Submit] -> [Validate] -> [Queue] -> [Execute] -> [Checkpoint] -> [Verify] -> [Complete]
                      |           |           |
                      v           v           v
                   [Reject]    [Pause]    [Retry]
```

#### Context Injection

Each task receives fresh context from:
- Task spec file (from WORK/ directory)
- Shared resources (from SHARED/ directory)
- Execution context (conversation ID, task history)

---

### 2.3 Monitoring and Health

#### Metrics Collection

All execution metrics feed into Option A's observability stack:

| Metric | Source | Destination |
|--------|--------|-------------|
| **Task Duration** | Orchestrator | Prometheus |
| **Task Status** | Orchestrator | PostgreSQL |
| **Error Logs** | Task output | Loki |
| **Execution Trace** | Task lifecycle | Tempo |
| **Resource Usage** | Container stats | Prometheus |

#### Dashboard Queries

Example Grafana queries for execution monitoring:

```promql
# Tasks by status
sum by (status) (execution_tasks_total{plan_id="$plan_id"})

# Average task duration
rate(execution_task_duration_seconds_sum{plan_id="$plan_id"}[5m])

# Error rate
sum(rate(execution_errors_total{plan_id="$plan_id"}[5m]))

# Progress percentage
(execution_tasks_completed{plan_id="$plan_id"} / execution_tasks_total{plan_id="$plan_id"}) * 100
```

---

### 2.4 Notification System

#### Voice Notification Integration

Uses existing PAI voice server at `localhost:8888`. All events use same voice ID from settings.

```typescript
interface VoiceNotification {
  message: string;              // 8-16 words, speakable text
  title?: string;               // Default: "Autonomous Execution"
  voice_id?: string;            // Default: DAIDENTITY.VOICEID
  priority?: "low" | "normal" | "high";
}
```

#### Notification Router

```typescript
interface NotificationRouter {
  route(event: ExecutionEvent): void;

  // Routes events to channels based on type and duration
  rules: {
    taskStart: ["voice"];
    taskComplete: ["voice", "push_if_long"];
    taskFail: ["voice", "push", "discord"];
    phaseComplete: ["voice", "push"];
    executionComplete: ["voice", "push", "discord"];
  };
}
```

---

## 3. Integration with Option A

### 3.1 Conversation ID Tracking

#### PostgreSQL Schema Extension

Add to Option A's conversation tracking database:

```sql
-- Execution tracking table
CREATE TABLE executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id),
  plan_id UUID NOT NULL,
  status execution_status NOT NULL,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  total_tasks INT,
  completed_tasks INT DEFAULT 0,
  failed_tasks INT DEFAULT 0,
  metadata JSONB
);

-- Task execution log
CREATE TABLE execution_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  execution_id UUID NOT NULL REFERENCES executions(id),
  task_id VARCHAR(50) NOT NULL,
  title TEXT NOT NULL,
  status task_status NOT NULL,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  duration_seconds INT,
  verification_results JSONB,
  error_message TEXT,
  checkpoint_data JSONB
);

-- Indexes for correlation
CREATE INDEX idx_executions_conversation ON executions(conversation_id);
CREATE INDEX idx_execution_tasks_execution ON execution_tasks(execution_id);
CREATE INDEX idx_execution_tasks_status ON execution_tasks(status);
```

---

### 3.2 Pattern Extraction with Qdrant

#### Vector Collection Schema

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

collection_name = "execution_patterns"

# Collection configuration
qdrant.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=1536,  # OpenAI embedding size, or use mxbai-embed-large (1024)
        distance=Distance.COSINE
    ),
    # Payload indexing for filtering
    optimizers_config={
        "indexing_threshold": 20000
    },
    # Replicate for durability
    replication_factor=2
)

# Point structure
point = {
    "id": "exec-123",
    "vector": embedding,  # Generated from task description + outcome
    "payload": {
        "conversation_id": "uuid",
        "task_title": "Deploy MinIO container",
        "task_type": "deployment",
        "success": True,
        "duration_seconds": 120,
        "commands": ["docker compose up -d"],
        "errors": [],
        "timestamp": "2026-02-04T12:00:00Z"
    }
}
```

#### Pattern Extraction Pipeline

```python
class PatternExtractor:
    def extract_from_logs(self, logs: str) -> dict:
        """Extract structured patterns from execution logs"""
        return {
            "commands": self._extract_commands(logs),
            "errors": self._extract_errors(logs),
            "warnings": self._extract_warnings(logs),
            "file_operations": self._extract_file_ops(logs),
            "api_calls": self._extract_api_calls(logs)
        }

    def embed(self, pattern: dict) -> list[float]:
        """Generate embedding from pattern"""
        text = self._pattern_to_text(pattern)
        return self.embedding_service.embed(text)

    def store(self, execution_id: str, pattern: dict, vector: list[float]):
        """Store pattern in Qdrant"""
        qdrant.upsert(
            collection_name="execution_patterns",
            points=[PointStruct(
                id=execution_id,
                vector=vector,
                payload=pattern
            )]
        )
```

---

### 3.3 Recommendation Engine

#### Similarity Search

```python
class RecommendationEngine:
    def find_similar(self, task_description: str, limit: int = 3) -> list[dict]:
        """Find similar historical executions"""
        # Embed the query
        query_vector = self.embedding_service.embed(task_description)

        # Search Qdrant
        results = qdrant.search(
            collection_name="execution_patterns",
            query_vector=query_vector,
            query_filter=self._build_filter(),
            limit=limit,
            with_payload=True
        )

        return [
            {
                "execution_id": r.id,
                "similarity": r.score,
                "task_title": r.payload["task_title"],
                "success": r.payload["success"],
                "duration": r.payload["duration_seconds"],
                "commands": r.payload["commands"],
                "errors": r.payload["errors"]
            }
            for r in results
        ]
```

#### Recommendation Display

In Claude Code, when similar tasks found:

```
Found 3 similar executions from history:

1. [98% similar] "Deploy MinIO container" (SUCCESS, 2 minutes)
   Commands: docker compose up -d
   Last executed: 2026-02-03

2. [92% similar] "Deploy S3-compatible storage" (SUCCESS, 3 minutes)
   Commands: docker run -p 9000:9000 minio/minio
   Last executed: 2026-01-28

3. [87% similar] "Setup object storage" (FAILED, timeout)
   Error: Port 9000 already in use
   Last executed: 2026-01-15

Would you like to apply the successful approach from #1?
```

---

### 3.4 Integration Architecture Diagram

```
Claude Code Session
       |
       v
[Plan File: ROADMAP.md]
       |
       v
[Handoff Command]
       |
       +-------<Conversation ID>-------+
       |                               |
       v                               v
[External Orchestrator]        [Option A Stack]
       |                       |
       |                       +---> PostgreSQL (conversation metadata)
       |                       |
       |                       +---> Qdrant (pattern storage)
       |                       |
       v                       +---> Prometheus (metrics)
[Task Execution]
       |
       v
[Verification]
       |
       +-----> [Auto-Test Runner]
       |
       v
[Checkpoint/Complete]
       |
       +-----> [Voice Notification] -> localhost:8888
       |
       +-----> [Push Notification] -> ntfy.sh
       |
       v
[Pattern Extraction] -> [Embedding] -> [Qdrant Storage]
```

---

## 4. External Orchestration Options

### 4.1 Comparison Matrix

| Aspect | **Prefect** | **Temporal** | **Airflow** | **Custom** |
|--------|------------|--------------|------------|------------|
| **Type** | Workflow orchestration | Distributed execution | Batch scheduling | Custom implementation |
| **Language** | Python | Go | Python | TypeScript/Bun |
| **Learning Curve** | Low | High | Medium | N/A |
| **Docker Support** | Excellent | Excellent | Poor | Built-in |
| **Persistence** | Built-in | Built-in | Database | Custom |
| **Monitoring** | UI + API | UI + API | UI | Grafana integration |
| **Scalability** | Single node | Distributed | Single node | Custom |
| **Claude Integration** | SDK + CLI | SDK | CLI | Native MCP server |
| **Background Exec** | Yes (daemon) | Yes (worker) | Yes (scheduler) | Yes (service) |
| **Restart Recovery** | Automatic | Automatic | Manual | Custom |
| **Resource Requirements** | ~100MB | ~200MB | ~500MB | ~50MB |
| **Recommendation** | **RECOMMENDED** | Good option | Overkill | Viable for simple needs |

---

### 4.1 Prefect (Recommended)

#### Why Prefect

- **Python-native:** Easy integration with existing PAI tooling
- **Docker-first:** Built-in container execution
- **Flow paradigm:** Maps naturally to task-based plans
- **Auto-retry:** Built-in retry with exponential backoff
- **UI dashboard:** Local UI for monitoring
- **Small footprint:** ~100MB memory
- **MCP-friendly:** Can run as MCP server

#### Architecture

```python
from prefect import flow, task, get_run_logger
from prefect.docker import DockerImage

@task(retries=3, retry_delay_seconds=60)
def execute_execution_task(task_spec: dict, context: dict):
    """Execute a single atomic task with fresh context"""
    logger = get_run_logger()
    logger.info(f"Starting task: {task_spec['title']}")

    # Inject context and execute
    result = run_with_context(task_spec, context)

    # Run verification if available
    if task_spec.get('verification'):
        verify_result = run_verification(result, task_spec['verification'])
        result['verification'] = verify_result

    return result

@flow(name="autonomous-execution", persist_result=True)
def autonomous_execution_flow(plan: ExecutionPlan):
    """Execute autonomous plan with Prefect orchestration"""
    results = {}

    for task in plan.tasks:
        # Check dependencies
        if dependencies_met(task, results):
            results[task.id] = execute_execution_task(
                task,
                context={
                    'conversation_id': plan.conversationId,
                    'plan_id': plan.id,
                    'previous_results': results
                }
            )

    return results
```

#### Integration Points

| Integration | Method |
|-------------|--------|
| **Claude Code** | Prefect CLI via MCP server |
| **PostgreSQL** | Prefect result storage |
| **Qdrant** | Custom state handler for pattern extraction |
| **Prometheus** | Prefect metrics exporter |
| **Voice Server** | Callback on state change |

---

### 4.2 Temporal

#### Why Consider Temporal

- **Durable execution:** Guarantees completion across failures
- **Go-based:** Excellent performance and reliability
- **Activity model:** Clean separation of workflow and execution
- **Visibility:** Excellent tracing and debugging

#### Drawbacks

- **Higher complexity:** Steeper learning curve
- **More resources:** ~200MB for temporal server
- **Workflow language:** Requires defining workflows in Go or SDK

#### Sample Workflow

```go
package workflows

import (
    "time"
    "go.temporal.io/sdk/workflow"
)

func AutonomousExecution(ctx workflow.Context, plan ExecutionPlan) (*ExecutionResult, error) {
    result := &ExecutionResult{}

    for _, task := range plan.Tasks {
        // Check dependencies
        if !dependenciesMet(task, result) {
            continue
        }

        // Execute activity with retry
        ao := workflow.ActivityOptions{
            StartToCloseTimeout: 30 * time.Minute,
            RetryPolicy: &temporal.RetryPolicy{
                InitialInterval:    time.Second,
                BackoffCoefficient: 2.0,
                MaximumAttempts:    3,
            },
        }
        ctx = workflow.WithActivityOptions(ctx, ao)

        var taskResult TaskResult
        err := workflow.ExecuteActivity(ctx, ExecuteTask, task).Get(ctx, &taskResult)
        if err != nil {
            return nil, err
        }

        result.Tasks = append(result.Tasks, taskResult)
    }

    return result, nil
}
```

---

### 4.3 Airflow

#### Why Airflow Might Not Fit

- **Batch-oriented:** Designed for scheduled ETL, not ad-hoc execution
- **Heavy footprint:** ~500MB+ with database
- **Python 2/3 legacy:** Some compatibility issues
- **Scheduler model:** Not ideal for on-demand execution

**Verdict:** Airflow is overkill for this use case. Choose Prefect instead.

---

### 4.4 Custom Implementation

#### When to Build Custom

- Need minimal resource footprint (<50MB)
- Want full control over execution model
- Building on existing PAI infrastructure
- Prefer TypeScript/JavaScript over Python

#### Architecture

```typescript
// Orchestrator service running as systemd/Docker
class AutonomousOrchestrator {
    private queue: ExecutionQueue;
    private store: ExecutionStore;  // PostgreSQL
    private notifier: NotificationService;

    async submitPlan(plan: ExecutionPlan): Promise<string> {
        // Validate and queue
        await this.store.save(plan);
        await this.queue.enqueue(plan);
        return plan.id;
    }

    async start(): Promise<void> {
        // Background worker
        while (true) {
            const plan = await this.queue.dequeue();
            if (plan) {
                this.executePlan(plan).catch(err => this.notifier.error(err));
            }
            await sleep(1000);
        }
    }

    private async executePlan(plan: ExecutionPlan): Promise<void> {
        const executor = new PlanExecutor(plan, {
            onTaskComplete: (task) => this.notifier.taskComplete(task),
            onTaskFail: (task, error) => this.notifier.taskFail(task, error),
            onPhaseComplete: (phase) => this.notifier.phaseComplete(phase)
        });

        await executor.run();
    }
}
```

#### Pros

- Full control over behavior
- TypeScript integration
- Minimal dependencies
- Can expose as MCP server

#### Cons

- Need to implement retry, recovery, monitoring
- More development effort
- Need to test thoroughly

---

## 5. Testing/Validation Automation

### 5.1 Auto-Test Runner Architecture

```typescript
interface TestRunner {
    // Discover and run tests for a task
    run(task: ExecutionTask, context: ExecutionContext): Promise<TestResult>;

    // Check if tests exist for task
    hasTests(task: ExecutionTask): boolean;
}

interface TestResult {
    passed: boolean;
    totalTests: number;
    passedTests: number;
    failedTests: number;
    duration: number;
    coverage?: number;
    failures: TestFailure[];
}

interface TestFailure {
    test: string;
    error: string;
    stack?: string;
}
```

#### Test Discovery

```
Task: "Deploy MinIO container"
      |
      v
Check for test files:
- tests/integration/minio.test.ts
- tests/e2e/minio-deployment.spec.ts
- tests/unit/minio-config.test.ts
      |
      v
If found: Run test suite
If not found: Mark as manual verification
```

---

### 5.2 Validation Gates

#### Gate Types

```typescript
interface ValidationGate {
    name: string;
    trigger: "pre" | "mid" | "post";
    condition: () => Promise<boolean>;
    onFail: "halt" | "warn" | "continue";
    action: () => Promise<void>;
}

// Example gates
const gates: ValidationGate[] = [
    {
        name: "Prerequisites Check",
        trigger: "pre",
        condition: checkPrerequisites,
        onFail: "halt",
        action: reportMissingPrerequisites
    },
    {
        name: "Disk Space",
        trigger: "mid",
        condition: () => checkDiskSpace(1024 * 1024 * 1024), // 1GB
        onFail: "warn",
        action: sendDiskSpaceWarning
    },
    {
        name: "Post-deployment Health",
        trigger: "post",
        condition: checkServiceHealth,
        onFail: "halt",
        action: rollbackDeployment
    }
];
```

---

### 5.3 Evaluation Metrics

#### Metrics to Collect

| Category | Metric | Collection Method |
|----------|--------|------------------|
| **Performance** | Task duration | Orchestrator timer |
| **Quality** | Test pass rate | Test runner output |
| **Reliability** | Success/failure ratio | Execution history |
| **Efficiency** | Context tokens used | LLM API metrics |
| **User Satisfaction** | Rating (1-10) | Manual feedback |

#### Metrics Storage

```sql
CREATE TABLE execution_metrics (
    id UUID PRIMARY KEY,
    execution_id UUID REFERENCES executions(id),
    task_id VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    unit VARCHAR(20),
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Materialized view for trends
CREATE MATERIALIZED VIEW metric_trends AS
SELECT
    DATE_TRUNC('day', collected_at) as day,
    metric_name,
    AVG(metric_value) as avg_value,
    COUNT(*) as sample_count
FROM execution_metrics
GROUP BY day, metric_name;
```

---

## 6. Architecture Options

### 6.1 Option A: Prefect-Based (Recommended)

#### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
│  - Creates plan (ROADMAP.md)                                │
│  - Invokes handoff command                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                  Prefect MCP Server                         │
│  - Accepts plan via MCP                                     │
│  - Deploys flow to Prefect daemon                           │
│  - Returns execution ID                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                Prefect Daemon                               │
│  - Queue: PostgreSQL                                        │
│  - Execution: Worker processes                              │
│  - State: Result storage                                    │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├─> [Task Execution] ──> [Verification] ──> [Checkpoint]
       │                                                        │
       v                                                        v
┌─────────────────────┐                              ┌──────────────────┐
│  Pattern Extractor   │                              │ Voice Notifier   │
│  - Parse logs        │                              │ - localhost:8888 │
│  - Embed vectors     │                              │ - ntfy.sh        │
│  - Store in Qdrant   │                              └──────────────────┘
└─────────────────────┘
```

#### Resource Requirements

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| Prefect Server | 0.5 | 256MB | 100MB |
| Prefect Worker | 1 | 512MB | 50MB |
| PostgreSQL (shared) | - | - | - |
| **Total** | 1.5 | 768MB | 150MB |

---

### 6.2 Option B: Custom TypeScript Orchestrator

#### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
│  - Creates plan                                              │
│  - Calls orchestrator MCP                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│              Autonomous Orchestrator (TS)                    │
│  - Bun runtime                                               │
│  - Job queue: in-memory or Redis                             │
│  - State: PostgreSQL                                         │
│  - Worker pool: processes                                    │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├─> [Worker Process] ──> [Task Execution]
       │                             │
       v                             v
┌─────────────────────┐      ┌──────────────────┐
│  Checkpointer        │      │ Notifier Module  │
│  - State persistence │      │ - Voice          │
│  - Resume capability │      │ - Push           │
└─────────────────────┘      │ - Discord        │
                             └──────────────────┘
```

#### Resource Requirements

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| Orchestrator Service | 0.5 | 128MB | 50MB |
| Worker (per concurrent) | 1 | 256MB | 20MB |
| **Total (2 workers)** | 2.5 | 640MB | 90MB |

---

### 6.3 Architecture Decision Matrix

| Criterion | Prefect | Custom TS |
|-----------|---------|-----------|
| **Development Time** | Low (existing tool) | High (build from scratch) |
| **Maintenance** | Low (community support) | High (custom code) |
| **Flexibility** | Medium | High |
| **Integration** | SDK + CLI | Native MCP |
| **Resource Usage** | ~768MB | ~640MB |
| **Reliability** | High (battle-tested) | Medium (needs testing) |
| **Learning Curve** | Low (Python) | Medium (TypeScript) |
| **Recommendation** | **YES for phase 1** | Consider for phase 2 |

---

## 7. Success Criteria

### 7.1 Functional Requirements

| ID | Requirement | Verification Method |
|----|-------------|---------------------|
| FR-1 | Accept ROADMAP.md plans | Submit plan, verify parsing |
| FR-2 | Execute tasks in background | Close Claude, verify continuation |
| FR-3 | Persist state across restarts | Kill orchestrator, restart, verify resume |
| FR-4 | Send voice notifications | Execute task, hear voice announcement |
| FR-5 | Store patterns in Qdrant | Complete task, query Qdrant for pattern |
| FR-6 | Auto-run available tests | Complete task with tests, verify execution |
| FR-7 | Correlate with conversation ID | Query PostgreSQL by conversation ID |

### 7.2 Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1 | Orchestrator availability | 99.9% | Uptime monitoring |
| NFR-2 | Task execution overhead | <5% | Duration comparison |
| NFR-3 | State recovery time | <30s | Restart test |
| NFR-4 | Notification latency | <5s | Timestamp delta |
| NFR-5 | Pattern extraction time | <10s | Post-task timing |
| NFR-6 | Resource usage | <1GB RAM | Container metrics |

### 7.3 Integration Requirements

| ID | System | Requirement | Verification |
|----|--------|-------------|--------------|
| IR-1 | Option A PostgreSQL | Store execution metadata | Query conversation_executions table |
| IR-2 | Option A Qdrant | Store execution patterns | Similarity search returns results |
| IR-3 | Voice Server | Send notifications | curl test succeeds |
| IR-4 | Prometheus | Export metrics | Query execution_* metrics |
| IR-5 | Loki | Stream task logs | View logs in Grafana |

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Tasks:**
1. Deploy Prefect server and worker
2. Create execution plan parser (ROADMAP.md -> Prefect flow)
3. Implement basic task executor (CLI invocation)
4. Setup PostgreSQL execution tables
5. Create MCP server for Claude Code integration

**Deliverables:**
- Prefect server running on localhost
- Plan successfully parsed and executed
- Execution state stored in database
- Handoff command works from Claude Code

**Verification:**
- Submit plan, close Claude, verify completion
- Query PostgreSQL for execution record

---

### Phase 2: Notifications (Week 2)

**Tasks:**
1. Implement notification router
2. Integrate with voice server (localhost:8888)
3. Add ntfy.sh push notifications
4. Create phase transition events
5. Test all notification channels

**Deliverables:**
- Voice announcements on task events
- Push notifications for long tasks
- Discord alerts for failures

**Verification:**
- Execute plan, receive voice updates
- Trigger failure, receive alert

---

### Phase 3: Pattern Learning (Week 3)

**Tasks:**
1. Deploy Qdrant container
2. Create pattern extraction pipeline
3. Implement embedding generation
4. Build similarity search API
5. Create recommendation engine

**Deliverables:**
- Execution patterns stored in Qdrant
- Historical execution search working
- Recommendations shown in Claude Code

**Verification:**
- Complete task, query Qdrant for pattern
- Search similar tasks, receive recommendations

---

### Phase 4: Testing Automation (Week 4)

**Tasks:**
1. Create test discovery mechanism
2. Implement auto-test runner
3. Add validation gates
4. Build evaluation metrics collector
5. Create test result dashboard

**Deliverables:**
- Tests auto-run after task completion
- Validation gates enforce quality
- Metrics collected and trended

**Verification:**
- Complete task with tests, verify execution
- Fail validation gate, verify halt

---

### Phase 5: Production Hardening (Week 5)

**Tasks:**
1. Add retry logic with exponential backoff
2. Implement checkpoint/resume
3. Create health check endpoints
4. Add graceful shutdown handling
5. Write comprehensive documentation

**Deliverables:**
- System survives restart
- Tasks retry on failure
- Health monitoring active

**Verification:**
- Kill orchestrator mid-execution, verify resume
- Trigger failure, verify retry

---

## Appendix A: File Locations

### Directory Structure

```
~/autonomous-execution/
├── docker-compose.yml          # Prefect + Qdrant services
├── orchestrator/
│   ├── main.ts                 # Custom orchestrator (if applicable)
│   ├── mcp-server.ts           # MCP interface for Claude Code
│   └── notification/
│       ├── voice.ts            # Voice server integration
│       └── router.ts           # Notification routing
├── flows/
│   └── autonomous_flow.py      # Prefect flow definition
├── pattern-extraction/
│   ├── extractor.py            # Log parsing and pattern extraction
│   └── embeddings.py           # Vector generation
├── tests/
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
└── docs/
    └── api.md                  # API documentation
```

### Environment Variables

```bash
# .env
PREFECT_API_URL=http://localhost:4200
PREFECT_API_KEY=              # Optional for local
QDRANT_HOST=localhost
QDRANT_PORT=6333
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=openclaw
POSTGRES_USER=openclaw
POSTGRES_PASSWORD=            # From secrets
VOICE_SERVER_URL=http://localhost:8888
NTFY_TOPIC=                   # From settings
DISCORD_WEBHOOK=              # Optional
```

---

## Appendix B: API Specification

### B.1 Handoff Endpoint

```typescript
// POST /api/execution/handoff
interface HandoffRequest {
  plan: ExecutionPlan;
  options: {
    priority?: "low" | "normal" | "high";
    notifications?: {
      voice?: boolean;
      push?: boolean;
      discord?: boolean;
    };
    retry?: {
      maxAttempts: number;
      backoffMultiplier: number;
    };
  };
}

interface HandoffResponse {
  executionId: string;
  status: "queued" | "running" | "failed";
  estimatedDuration: number;
  webhookUrl: string;  // For status updates
}
```

### B.2 Status Endpoint

```typescript
// GET /api/execution/:id/status
interface StatusResponse {
  executionId: string;
  status: "running" | "completed" | "failed" | "paused";
  progress: {
    current: number;
    total: number;
    percentage: number;
  };
  currentTask?: {
    id: string;
    title: string;
    startedAt: string;
  };
  completedTasks: string[];
  failedTasks: string[];
  eta?: string;
}
```

### B.3 Control Endpoint

```typescript
// POST /api/execution/:id/control
interface ControlRequest {
  action: "pause" | "resume" | "cancel" | "retry";
  taskId?: string;  // For retry action
}

interface ControlResponse {
  success: boolean;
  message: string;
}
```

---

## Appendix C: Migration from Option A

### C.1 Component Integration

This system integrates with Option A components as follows:

| Option A Component | Integration Point | Data Flow |
|--------------------|-------------------|-----------|
| **Prometheus** | Metrics exporter | Execution metrics → Prometheus |
| **Loki** | Log streaming | Task output → Loki |
| **Grafana** | Dashboard | Metrics + logs → dashboards |
| **PostgreSQL** | Execution storage | Conversation + execution records |
| **Qdrant** | Pattern storage | Execution patterns → vectors |
| **MinIO** | Artifact storage | Task outputs → S3 buckets |

### C.2 Deployment

Add to Option A docker-compose:

```yaml
services:
  # ... existing Option A services ...

  autonomous-executor:
    image: prefecthq/prefect:3-latest
    command: prefect server start
    ports:
      - "4200:4200"
    environment:
      - PREFECT_API_URL=http://localhost:4200/api
      - PREFECT_UI_API_URL=http://localhost:4200/api
      - POSTGRES_CONNECTION_STRING=postgresql://openclaw:${POSTGRES_PASSWORD}@postgres:5432/openclaw
    depends_on:
      - postgres

  prefect-worker:
    image: prefecthq/prefect:3-latest
    command: prefect worker start -p default-worker
    environment:
      - PREFECT_API_URL=http://autonomous-executor:4200/api
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - autonomous-executor
```

---

*Document End*

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-04 | 1.0 | Initial requirements document |
