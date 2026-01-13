# Document Refiner Agent - Ralph Loop for Living Documentation

> **File**: `scripts/doc-refiner.py` (v1.2 Phase 4B)
> **Purpose**: Keep `.claude/*.md` files synchronized with codebase changes
> **Philosophy**: Ralph Loop - continuous refinement based on usage + code changes
> **Trigger**: Background daemon, cron job, or manual invocation
> **Status**: Design phase (follows Foraging Agent)

---

## The Problem

**Current state:**
```
1. User creates .claude/modules/pipeline.md describing pipeline.py
2. Developer modifies pipeline.py (adds features, refactors)
3. Documentation becomes stale
4. Claude gets outdated context
5. Manual updates required (often forgotten)
```

**Symptoms of stale docs:**
- Low usefulness scores (injected but not helpful)
- Claude asks questions that docs should answer
- Edits to source files that docs claim don't exist
- Confusion about actual vs documented architecture

---

## The Solution: Background Refinement Agent

**Continuous improvement loop:**
```
while True:
    # Detect changes
    changed_files = detect_file_changes()

    # Find affected docs
    affected_docs = find_docs_describing(changed_files)

    # Analyze staleness
    staleness = calculate_staleness(affected_docs)

    # For stale docs: propose refinements
    if staleness > threshold:
        proposals = generate_refinement_proposals(doc)

        # Ralph Loop: Test proposals
        apply_proposal()
        measure_improvement()

        if improved:
            commit_refinement()
        else:
            rollback()
            try_different_approach()

    # Sleep until next check
    sleep(interval)
```

---

## Trigger Modes

### Mode 1: File Watcher (Real-time)

**Use case:** Aggressive keeping docs fresh

```python
# Watch source files for changes
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SourceFileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            # Find .md files that describe this source
            md_files = find_related_md_files(event.src_path)

            for md_file in md_files:
                # Mark for refinement
                enqueue_refinement(md_file, reason="source_changed")

# Start watching
observer = Observer()
observer.schedule(SourceFileChangeHandler(), ".", recursive=True)
observer.start()
```

**Pros:**
- Immediate detection of staleness
- Docs stay synchronized in real-time
- No manual triggers needed

**Cons:**
- May be too aggressive (frequent churn)
- CPU overhead from file watching
- Could interrupt workflow

---

### Mode 2: Cron Job (Periodic)

**Use case:** Daily/weekly refinement checks

```bash
# Add to crontab
# Run every night at 2am
0 2 * * * cd ~/project && python3 ~/.claude/scripts/doc-refiner.py

# Or weekly on Sunday
0 2 * * 0 cd ~/project && python3 ~/.claude/scripts/doc-refiner.py --aggressive
```

**Pros:**
- Predictable overhead (off-hours)
- Batched refinements (more efficient)
- Can run comprehensive analysis

**Cons:**
- Delay between changes and updates
- May miss rapid iteration periods
- Requires cron setup

---

### Mode 3: Manual Invocation (On-demand)

**Use case:** Developer-triggered refinement

```bash
# Check what's stale
$ python3 scripts/doc-refiner.py --check

Staleness Report:
  ⚠️  modules/pipeline.md (stale: 7 days, 42 commits since update)
  ⚠️  systems/network.md (stale: 3 days, 12 commits since update)
  ✅  modules/usage-tracker.md (fresh: updated today)

# Refine stale docs
$ python3 scripts/doc-refiner.py --refine

Refining modules/pipeline.md...
  - Source file changed: scripts/refined_pipeline_integrated_v4_fixed.py
  - Detected new function: handle_anticipatory_coherence()
  - Detected removed section: old_module_loading()

  Proposal: Add section on anticipatory coherence integration
  Apply? [y/N/preview]: preview

  [Shows proposed changes...]

  Apply? [y/N]: y
  ✅ Refined modules/pipeline.md (iteration 3)
```

**Pros:**
- Developer control over timing
- Preview before applying
- Can target specific docs

**Cons:**
- Requires manual memory
- May be forgotten during rapid dev

---

## Ralph Loop Integration

### Phase 1: Detect Staleness

**Objective metrics:**
```python
def calculate_staleness(md_file: Path, source_files: List[Path]) -> float:
    """
    Calculate staleness score (0.0 = fresh, 1.0 = very stale)
    """
    factors = []

    # Factor 1: Time since last update
    days_since_update = (now() - md_file.stat().st_mtime) / 86400
    time_score = min(days_since_update / 30, 1.0)  # Cap at 30 days
    factors.append(time_score * 0.3)  # 30% weight

    # Factor 2: Source file commits since doc update
    commits = count_commits_since(source_files, md_file.stat().st_mtime)
    commit_score = min(commits / 50, 1.0)  # Cap at 50 commits
    factors.append(commit_score * 0.4)  # 40% weight

    # Factor 3: Usefulness decline
    current_usefulness = get_usefulness(md_file)
    historical_avg = get_historical_usefulness(md_file)
    if historical_avg > 0:
        usefulness_decline = max(0, historical_avg - current_usefulness) / historical_avg
        factors.append(usefulness_decline * 0.3)  # 30% weight

    return sum(factors)
```

---

### Phase 2: Generate Refinement Proposals

**Detection strategies:**

```python
def generate_refinement_proposals(md_file: Path, source_files: List[Path]):
    """
    Analyze source changes and propose doc updates.
    """
    proposals = []

    # Strategy 1: New functions/classes
    new_entities = detect_new_entities(source_files, since=md_file.stat().st_mtime)
    if new_entities:
        proposals.append({
            'type': 'add_section',
            'reason': f'New functions detected: {", ".join(new_entities)}',
            'content': generate_function_docs(new_entities)
        })

    # Strategy 2: Removed/renamed entities
    removed = detect_removed_entities(md_file, source_files)
    if removed:
        proposals.append({
            'type': 'remove_section',
            'reason': f'Entities no longer exist: {", ".join(removed)}',
            'sections': find_sections_mentioning(removed)
        })

    # Strategy 3: Changed signatures
    changed_sigs = detect_signature_changes(source_files, since=md_file.stat().st_mtime)
    if changed_sigs:
        proposals.append({
            'type': 'update_signature',
            'reason': f'Function signatures changed',
            'updates': generate_signature_updates(changed_sigs)
        })

    # Strategy 4: Low usefulness → needs better keywords
    if get_usefulness(md_file) < 0.5:
        proposals.append({
            'type': 'improve_keywords',
            'reason': 'Low usefulness score - may need better discoverability',
            'suggestions': extract_important_terms(source_files)
        })

    return proposals
```

---

### Phase 3: Test & Measure

**Ralph Loop: Try proposal, measure impact**

```python
def test_refinement_proposal(md_file: Path, proposal: dict):
    """
    Apply proposal temporarily, measure if it improves usefulness.
    """
    # Backup original
    backup = md_file.read_text()

    try:
        # Apply proposal
        apply_proposal(md_file, proposal)

        # Mark as test iteration
        mark_test_iteration(md_file, proposal)

        # Wait for usage data (use during next session)
        # This is async - agent checks back later
        schedule_evaluation(md_file, proposal, after_turns=10)

    except Exception as e:
        # Rollback on error
        md_file.write_text(backup)
        log_failure(md_file, proposal, e)
```

**Evaluation after test period:**

```python
def evaluate_refinement(md_file: Path, proposal: dict, test_start: datetime):
    """
    After 10 turns of usage, evaluate if refinement helped.
    """
    # Get usefulness before/after
    usefulness_before = get_usefulness_before(md_file, test_start)
    usefulness_after = get_usefulness_after(md_file, test_start)

    improvement = usefulness_after - usefulness_before

    if improvement > 0.1:  # 10% improvement
        # Success! Keep the refinement
        finalize_refinement(md_file, proposal)
        log_success(md_file, proposal, improvement)

    elif improvement < -0.1:  # Made it worse!
        # Rollback
        rollback_refinement(md_file, proposal)
        log_failure(md_file, proposal, improvement)

    else:
        # Neutral - keep but note uncertain value
        mark_uncertain(md_file, proposal)
```

---

### Phase 4: Learn & Improve

**Meta-learning: Which refinement strategies work best?**

```python
def analyze_refinement_effectiveness():
    """
    Learn which types of proposals actually improve usefulness.
    """
    history = load_refinement_history()

    # Group by proposal type
    by_type = {}
    for refinement in history:
        proposal_type = refinement['proposal']['type']
        if proposal_type not in by_type:
            by_type[proposal_type] = []
        by_type[proposal_type].append(refinement['improvement'])

    # Calculate success rate per type
    for ptype, improvements in by_type.items():
        success_rate = len([i for i in improvements if i > 0.1]) / len(improvements)
        avg_improvement = sum(improvements) / len(improvements)

        print(f"{ptype}:")
        print(f"  Success rate: {success_rate:.1%}")
        print(f"  Avg improvement: {avg_improvement:+.2f}")

    # Adjust strategy weights
    adjust_proposal_weights(by_type)
```

**Example output:**
```
Refinement Strategy Effectiveness:

add_section:
  Success rate: 68%
  Avg improvement: +0.15
  → Increase weight to 1.2

remove_section:
  Success rate: 82%
  Avg improvement: +0.22
  → Increase weight to 1.4

update_signature:
  Success rate: 45%
  Avg improvement: +0.03
  → Decrease weight to 0.8

improve_keywords:
  Success rate: 91%
  Avg improvement: +0.31
  → Increase weight to 1.6 (most effective!)
```

---

## Circuit Breakers

**Safety limits to prevent runaway refinement:**

### 1. Rate Limiting
```python
MAX_REFINEMENTS_PER_DAY = 5
MAX_REFINEMENTS_PER_DOC = 1  # per day

if refinements_today() >= MAX_REFINEMENTS_PER_DAY:
    log("Rate limit reached - postponing refinements")
    return
```

### 2. Confidence Threshold
```python
MIN_CONFIDENCE_FOR_AUTO_APPLY = 0.8

if proposal['confidence'] < MIN_CONFIDENCE_FOR_AUTO_APPLY:
    # Require manual approval
    notify_user(proposal)
    await_approval()
```

### 3. Change Magnitude Limit
```python
MAX_CHANGES_PER_REFINEMENT = 100  # lines

if len(proposal['diff'].split('\n')) > MAX_CHANGES_PER_REFINEMENT:
    log("Proposal too large - splitting into smaller changes")
    split_proposal()
```

### 4. Rollback on Degradation
```python
DEGRADATION_THRESHOLD = -0.05  # 5% worse

if improvement < DEGRADATION_THRESHOLD:
    rollback_immediately(md_file)
    log("Emergency rollback - refinement made things worse")
```

---

## Integration with Usage Tracker

**Shared data structures:**

```python
# Usage tracker provides usefulness scores
from usage_tracker import UsageTracker

tracker = UsageTracker(mode='observe')

# Doc refiner uses those scores to guide refinements
def should_refine(md_file: Path) -> bool:
    usefulness = tracker.calculate_usefulness(md_file)
    staleness = calculate_staleness(md_file)

    # Refine if:
    # 1. Stale AND previously useful (may have drifted)
    # 2. Fresh but low usefulness (needs improvement)
    return (staleness > 0.5 and usefulness > 0.5) or \
           (staleness < 0.3 and usefulness < 0.3)
```

**Feedback loop:**
```
Usage Tracker → Usefulness scores
       ↓
Doc Refiner → Refinement proposals
       ↓
Apply refinement
       ↓
Usage Tracker → Measure new usefulness
       ↓
Doc Refiner → Learn which refinements work
```

---

## CLI Interface

```bash
# Check staleness
$ doc-refiner check
📊 Staleness Report:
  ⚠️  HIGH: modules/pipeline.md (staleness: 0.82)
  ⚠️  MEDIUM: systems/network.md (staleness: 0.54)
  ✅  FRESH: modules/usage-tracker.md (staleness: 0.08)

# Preview refinements
$ doc-refiner preview modules/pipeline.md
🔍 Analyzing modules/pipeline.md...

Proposal 1: Add section for anticipatory coherence
  Confidence: 0.85
  Reason: New integration detected in source

  + ## Anticipatory Coherence Integration
  + The pipeline now integrates with ACF (Anticipatory Coherence Field)
  + for trajectory-based routing decisions...

Proposal 2: Update process_message signature
  Confidence: 0.92
  Reason: Function signature changed

  - def process_message(user_id, text):
  + def process_message(user_id, text, context=None):

# Apply refinements (with approval)
$ doc-refiner refine modules/pipeline.md
Applying 2 proposals...
  ✅ Added section: Anticipatory Coherence Integration
  ✅ Updated signature: process_message

Refinement complete (iteration 4)
Scheduling evaluation after 10 turns...

# Auto-refine all stale docs
$ doc-refiner auto
🤖 Auto-refining stale documentation...
  Scanning .claude/ for stale docs...
  Found 3 stale docs above threshold (0.5)

  Refining modules/pipeline.md... ✅
  Refining systems/network.md... ✅
  Refining modules/gto-adapters.md... ⏭️ (confidence too low, skipped)

Done! Refined 2/3 docs. Check .claude/refinement_log.txt

# Start background daemon
$ doc-refiner daemon --interval 3600
🔄 Document refiner daemon starting...
  Mode: periodic
  Interval: 3600 seconds (1 hour)
  Watching: .claude/ and project files

  [2026-01-08 16:00] Scan 1: No stale docs
  [2026-01-08 17:00] Scan 2: Refined modules/pipeline.md
  [2026-01-08 18:00] Scan 3: No stale docs
  ^C
  Daemon stopped.
```

---

## Success Metrics

**How to know if doc refinement is working:**

### 1. Usefulness Trend

```
Goal: Docs maintain high usefulness over time

modules/pipeline.md usefulness history:
  Week 1: 0.85 (initial creation)
  Week 2: 0.78 (slight drift)
  Week 3: 0.82 (refinement applied ✅)
  Week 4: 0.84 (stable)
```

### 2. Staleness Distribution

```
Goal: Most docs stay fresh (<0.3 staleness)

Staleness distribution:
  Fresh (0.0-0.3): 85% of docs ✅
  Medium (0.3-0.6): 12% of docs
  Stale (0.6-1.0): 3% of docs
```

### 3. Manual Update Frequency

```
Goal: Reduce manual doc updates by 80%

Manual updates per month:
  Before doc-refiner: 15 manual edits
  After doc-refiner: 3 manual edits
  Reduction: 80% ✅
```

### 4. Refinement Success Rate

```
Goal: >70% of refinements improve usefulness

Refinements last 30 days: 42 applied
Improved usefulness: 31 (74%) ✅
No change: 8 (19%)
Degraded: 3 (7%, all rolled back)
```

---

## Phase Roadmap

### Phase 4A: Basic Detection (Week 7)
- File change detection (git commits)
- Staleness calculation
- Manual invocation only

### Phase 4B: Proposal Generation (Week 7-8)
- AST analysis for code changes
- Refinement proposal generation
- Preview mode

### Phase 4C: Auto-Refinement (Week 8)
- Apply proposals automatically
- Measure usefulness impact
- Rollback on degradation

### Phase 4D: Background Daemon (Week 9)
- File watcher mode
- Cron job mode
- Meta-learning on refinement effectiveness

### Phase 4E: Polish (Week 10)
- LLM-assisted proposal generation
- Interactive approval workflow
- Integration with foraging agent

---

## Ralph Loop Validation

**This is pure Ralph Loop thinking:**

1. **Iterate**: Don't expect docs to stay perfect forever
2. **Feedback**: Measure usefulness objectively (not subjective quality)
3. **Learn**: Track which refinement strategies actually work
4. **Refine**: Apply successful strategies more, abandon unsuccessful ones
5. **Converge**: Over time, refinements become less frequent as docs stabilize

**Anti-patterns avoided:**
- ❌ One-shot perfect documentation (impossible)
- ❌ Manual synchronization (forgotten)
- ❌ Subjective quality metrics (can't optimize)
- ❌ No rollback mechanism (refinements can make things worse)

**Ralph Loop patterns embraced:**
- ✅ Continuous iteration
- ✅ Objective feedback (usefulness scores)
- ✅ Automatic learning from outcomes
- ✅ Safe experimentation with rollback
- ✅ Circuit breakers prevent runaway behavior

---

## Example: Living Documentation in Action

**Day 1:** Developer adds anticipatory coherence to pipeline.py

**Day 2 (2am):** Doc refiner cron job runs
```
Detected: pipeline.py changed (15 commits since doc update)
Staleness: 0.68 (high)
Generating proposals...
  Proposal: Add section on anticipatory coherence integration
  Confidence: 0.85
  Auto-applying (confidence > 0.8 threshold)
✅ Refined modules/pipeline.md
```

**Day 3-5:** Usage tracking observes the refined doc
```
Turn 8: injected pipeline.md → Claude read pipeline.py
Turn 12: injected pipeline.md → Claude edited acf.py (related!)
Turn 19: injected pipeline.md → Claude asked about ACF (doc helped!)
```

**Day 6:** Evaluation completes
```
Usefulness before refinement: 0.78
Usefulness after refinement: 0.89
Improvement: +0.11 ✅

Action: Finalize refinement (success!)
Meta-learning: "add_section" strategy effectiveness +0.11
```

**Day 30:** The doc stays current without manual intervention
```
Refinements applied: 4
Success rate: 100%
Manual edits needed: 0
Developer satisfaction: "I forgot docs can stay current automatically!"
```

---

**Status**: Ready to build after Phase 4A (Foraging Agent) completes
**Dependencies**: Usage Tracker (for usefulness scores), Git (for change detection)
**Estimated effort**: 1-2 weeks after foraging agent
**Ralph Loop score**: 10/10 (pure iteration + feedback + learning)
