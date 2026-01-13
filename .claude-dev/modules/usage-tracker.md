# Usage Tracker - Learning from Actual Behavior

> **File**: `scripts/usage-tracker.py` (v1.2 Phase 1)
> **Purpose**: Track which injected files Claude actually uses, enabling learning
> **Philosophy**: Measure objective utility, not assumed relevance
> **Status**: Design phase → Prototype → Integration

---

## The Problem

**Current v1.1 behavior:**
```
Turn 47: Inject pipeline.md, orin.md, asus.md (HOT)
Claude uses: pipeline.md
Result: 66% of injected context wasted

Turn 48: Same 3 files still HOT
Claude uses: pipeline.md again
Result: Still wasting 2/3 of budget
```

**Why this matters:**
- Wasted token budget on unused files
- Could inject more useful files instead
- Keywords activate files that aren't actually helpful
- No feedback loop to improve over time

---

## The Solution

**Track objective usage:**
```
What was injected? → What did Claude access? → Calculate usefulness
    ↓                       ↓                           ↓
pipeline.md           Read pipeline.md             100% useful
orin.md              (never accessed)              0% useful
asus.md              (never accessed)              0% useful
    ↓
Learn: Lower weight on "orin" and "asus" keywords for this context
```

**Ralph Loop Pattern:**
```
Inject context → Track usage → Measure usefulness → Adjust weights → Inject (repeat)
```

---

## What to Track

### Per-Turn Data

```python
{
  "turn": 47,
  "timestamp": "2026-01-03T18:43:21Z",
  "instance_id": "A",

  # What was injected
  "injected_files": [
    {"file": "pipeline.md", "tier": "HOT", "score": 1.0, "chars": 12450},
    {"file": "orin.md", "tier": "HOT", "score": 0.92, "chars": 8320},
    {"file": "asus.md", "tier": "WARM", "score": 0.45, "chars": 1250}
  ],

  # What Claude actually did
  "tool_calls": [
    {"tool": "Read", "target": "scripts/pipeline.py", "timestamp": 0.5},
    {"tool": "Edit", "target": "scripts/pipeline.py", "timestamp": 12.3},
    {"tool": "Grep", "pattern": "process_message", "timestamp": 18.7}
  ],

  # Analysis
  "files_accessed": ["pipeline.md"],  # Inferred from tool calls
  "files_edited": [],
  "files_mentioned": ["pipeline.md"],  # Inferred from response text

  # Metrics
  "injection_rate": 0.33,  # 1/3 files accessed
  "budget_utilized": 0.56, # 12450/22020 chars were useful
  "wasted_budget": 0.44    # 44% injected but unused
}
```

### Cumulative Learning Data

```python
{
  "file": "pipeline.md",
  "statistics": {
    "injected_count": 127,      # Times injected (HOT or WARM)
    "accessed_count": 98,        # Times actually accessed
    "edited_count": 23,          # Times edited
    "mentioned_count": 87,       # Times mentioned in response

    "usefulness_score": 0.77,    # accessed/injected = 98/127
    "impact_score": 0.18,        # edited/injected = 23/127

    "last_injected": "2026-01-03T18:43:21Z",
    "last_accessed": "2026-01-03T18:42:15Z"
  },

  "keywords_triggered_by": {
    "pipeline": 45,   # Times "pipeline" keyword caused injection
    "process": 23,    # Times "process" keyword caused injection
    "message": 18     # Times "message" keyword caused injection
  },

  "co_activated_with": {
    "orin.md": 34,    # Times co-activated with orin.md
    "legion.md": 12
  }
}
```

---

## How to Infer Usage

**Challenge**: Claude Code doesn't explicitly report "I read pipeline.md"

**Solution**: Infer from tool calls

### 1. Direct File Access
```python
# Claude reads a file we injected
Tool: Read(file_path="scripts/pipeline.py")
Inference: pipeline.md was useful (describes pipeline.py)

Tool: Edit(file_path="scripts/context-router-v2.py")
Inference: context-router.md was very useful (high impact)
```

### 2. Related File Access
```python
# Injected: systems/orin.md (describes orin_client.py)
# Claude reads: scripts/orin_client.py
# Inference: orin.md was useful (provided context for that file)
```

### 3. Keyword/Pattern Matching
```python
# Injected: modules/pipeline.md
# Claude uses: Grep(pattern="process_message")
# pipeline.md mentions "process_message" → likely useful
```

### 4. Response Analysis
```python
# Injected: systems/orin.md
# Claude's response mentions: "The Orin sensory service..."
# Inference: orin.md provided useful context
```

### 5. Negative Signal (Unused)
```python
# Injected: asus.md (8KB, HOT)
# No tool calls accessing ASUS-related files
# No mentions of "asus" or "visual" in response
# Inference: asus.md was NOT useful (wasted budget)
```

---

## Mapping Injected .md → Actual Files

**Challenge**: Injected `systems/orin.md`, but Claude accesses `scripts/orin_client.py`

**Solution**: Maintain file relationship map

```python
FILE_RELATIONSHIPS = {
    "systems/orin.md": {
        "describes": [
            "scripts/orin_client.py",
            "bilateral_services/orin_service/**/*.py",
            # Patterns to match
        ],
        "keywords": ["orin", "layer 0", "sensory", "sentiment"],
        "integrations": ["integrations/pipe-to-orin.md"]
    },
    "modules/pipeline.md": {
        "describes": [
            "refined_pipeline_integrated_v4_fixed.py",
            "mirrorbot_cvmp_v80x.py"
        ],
        "keywords": ["pipeline", "process", "message"],
        "integrations": []
    }
}

# When Claude accesses scripts/orin_client.py:
# → Mark systems/orin.md as "useful"
```

**Auto-generation strategy:**
```python
# Extract from .md file content
for md_file in claude_md_files:
    content = md_file.read_text()

    # Find file references in backticks or code blocks
    file_refs = re.findall(r'`([a-zA-Z0-9_/.-]+\.py)`', content)

    # Extract keywords from headers and content
    keywords = extract_keywords(content)

    FILE_RELATIONSHIPS[md_file] = {
        "describes": file_refs,
        "keywords": keywords
    }
```

---

## Learning Algorithm

### Usefulness Score Calculation

```python
def calculate_usefulness(file_stats):
    """How useful is this file when injected?"""

    # Base metric: Access rate
    access_rate = file_stats.accessed_count / file_stats.injected_count

    # Bonus: High-impact actions (edits)
    impact_bonus = (file_stats.edited_count / file_stats.injected_count) * 0.5

    # Bonus: Mentioned in responses (proved useful)
    mention_bonus = (file_stats.mentioned_count / file_stats.injected_count) * 0.3

    # Combined usefulness score (0.0 to 1.0+)
    usefulness = access_rate + impact_bonus + mention_bonus

    return min(usefulness, 1.0)  # Cap at 1.0


# Example outcomes:
# File always accessed + often edited: 1.0 (extremely useful)
# File always accessed, rarely edited: 0.8-0.9 (very useful)
# File sometimes accessed: 0.4-0.6 (moderately useful)
# File rarely accessed: 0.1-0.3 (low utility)
# File never accessed: 0.0 (wasted injection)
```

### Keyword Weight Adjustment

```python
def adjust_keyword_weight(keyword, file, usefulness):
    """Learn which keywords produce useful activations"""

    # Current weight
    current_weight = KEYWORD_WEIGHTS.get(keyword, 1.0)

    # Learning rate (how fast to adapt)
    learning_rate = 0.1

    # Adjustment based on usefulness
    if usefulness > 0.75:  # Very useful
        new_weight = current_weight * (1 + learning_rate)
    elif usefulness < 0.25:  # Not useful
        new_weight = current_weight * (1 - learning_rate)
    else:  # Moderately useful
        new_weight = current_weight  # No change

    # Bounds checking
    new_weight = max(0.5, min(new_weight, 1.5))  # Keep in [0.5, 1.5]

    return new_weight


# Example learning:
# "pipeline" keyword → pipeline.md → 0.85 usefulness
# → Boost "pipeline" weight: 1.0 → 1.1

# "asus" keyword → asus.md → 0.15 usefulness
# → Lower "asus" weight: 1.0 → 0.9

# After 50 iterations:
# "pipeline": 1.4 (boosted, very useful)
# "asus": 0.6 (lowered, rarely useful in this project)
```

### Convergence Detection

```python
def detect_convergence(weight_history, window=50):
    """Know when to stop adjusting weights"""

    if len(weight_history) < window:
        return False, "Insufficient data"

    recent_weights = weight_history[-window:]

    # Check variance
    variance = np.var(recent_weights)
    if variance < 0.01:  # Very stable
        return True, "Weights converged (low variance)"

    # Check improvement rate
    improvement = (recent_weights[-1] - recent_weights[0]) / recent_weights[0]
    if abs(improvement) < 0.05:  # <5% change over window
        return True, "Weights stable (no improvement)"

    # Check oscillation
    changes = np.diff(recent_weights)
    sign_changes = np.sum(np.diff(np.sign(changes)) != 0)
    if sign_changes > window * 0.3:  # >30% sign changes
        return True, "Weights oscillating (no clear direction)"

    return False, "Continue learning"
```

---

## Integration Points

### 1. UserPromptSubmit Hook (Before)

```python
# scripts/context-router-v2.py

def user_prompt_submit_hook(prompt):
    # Existing: Compute attention scores, inject context
    context = inject_context(scores, budget=25000)

    # NEW: Record what was injected
    tracker.log_injection(
        turn=turn_number,
        injected_files=get_injected_files(scores),
        prompt=prompt
    )

    return context
```

### 2. Stop Hook (After)

```python
# NEW: scripts/usage-tracker.py (called from Stop hook)

def track_turn_usage(turn_data):
    """Analyze tool calls after turn completes"""

    # Parse tool calls from conversation
    tool_calls = extract_tool_calls(turn_data)

    # Infer which injected files were useful
    files_accessed = infer_file_usage(tool_calls, injected_files)

    # Update statistics
    update_usage_stats(files_accessed, injected_files)

    # Calculate metrics
    injection_rate = len(files_accessed) / len(injected_files)

    # Log for analysis
    log_usage_metrics(turn, injection_rate)

    # Every 50 turns, adjust weights
    if turn % 50 == 0:
        adjust_keyword_weights()
```

### 3. Context Router Integration

```python
# scripts/context-router-v2.py (modified)

def compute_attention_scores(query, current_scores):
    # Existing keyword matching
    base_scores = keyword_match(query)

    # NEW: Apply learned weights
    adjusted_scores = {}
    for file, score in base_scores.items():
        usefulness = tracker.get_usefulness(file)
        keyword_weight = tracker.get_keyword_weight(query, file)

        # Boost high-utility files, lower low-utility files
        adjusted_scores[file] = score * keyword_weight * usefulness

    return adjusted_scores
```

---

## Data Persistence

### File Structure

```
.claude/
├── usage_stats.json              # Per-file statistics
├── usage_history.jsonl           # Per-turn usage log
├── keyword_weights.json          # Learned keyword weights
└── learning_progress.txt         # Human-readable log
```

### usage_stats.json

```json
{
  "pipeline.md": {
    "injected_count": 127,
    "accessed_count": 98,
    "edited_count": 23,
    "usefulness_score": 0.77,
    "last_updated": "2026-01-03T18:43:21Z"
  },
  "orin.md": {
    "injected_count": 87,
    "accessed_count": 73,
    "usefulness_score": 0.84,
    "last_updated": "2026-01-03T18:42:15Z"
  }
}
```

### usage_history.jsonl

```json
{"turn": 47, "injected": ["pipeline.md", "orin.md"], "accessed": ["pipeline.md"], "rate": 0.5}
{"turn": 48, "injected": ["pipeline.md"], "accessed": ["pipeline.md"], "rate": 1.0}
```

### keyword_weights.json

```json
{
  "pipeline": 1.35,
  "orin": 1.42,
  "asus": 0.67,
  "visual": 0.73,
  "database": 1.18
}
```

### learning_progress.txt (Ralph Loop transparency)

```
[2026-01-03 18:45] Keyword Weight Adjustment (Turn 50)
  "pipeline" keyword:
    Previous weight: 1.0
    Usefulness: 0.85 (pipeline.md accessed 43/50 times)
    New weight: 1.1 (+10%)
    Reason: High utility, boost activation probability

  "asus" keyword:
    Previous weight: 1.0
    Usefulness: 0.15 (asus.md accessed 8/50 times)
    New weight: 0.9 (-10%)
    Reason: Low utility, reduce activation probability

  Overall metrics:
    Average injection rate: 0.68 (68% of injected files accessed)
    Budget utilization: 72% (up from 56% at turn 0)
    Convergence: Not yet (weights still adjusting >5% per window)

[2026-01-03 19:15] Keyword Weight Adjustment (Turn 100)
  "pipeline": 1.1 → 1.15 (+5%)
  "orin": 1.05 → 1.12 (+7%)
  "asus": 0.9 → 0.85 (-6%)

  Convergence check: Continue (improvement rate: 8% over last 50 turns)

[2026-01-03 20:30] Keyword Weight Adjustment (Turn 150)
  Weights stable:
    "pipeline": 1.15 → 1.16 (+1%)
    "orin": 1.12 → 1.13 (+1%)
    "asus": 0.85 → 0.84 (-1%)

  Convergence detected: Weights stabilized (<2% change over 50 turns)
  Action: Switching to monitoring mode (adjust every 100 turns instead of 50)
```

---

## Testing Strategy

### Phase 1: Track Without Acting

```python
# Test: Observe, don't adjust yet
tracker = UsageTracker(mode="observe")

# Run 100 turns on claude-cognitive project
# Log what would be adjusted, but don't change weights
# Validate inference logic is correct
```

### Phase 2: Adjust and Measure

```python
# Test: Enable learning
tracker = UsageTracker(mode="learn")

# Baseline: Measure context quality without usage tracking
baseline_metrics = measure_context_quality(turns=50)

# With tracking: Same 50 turns with learning enabled
tracking_metrics = measure_context_quality(turns=50, use_tracker=True)

# Compare:
# - Injection rate (should increase)
# - Budget utilization (should increase)
# - Wasted budget (should decrease)
```

### Phase 3: Convergence Testing

```python
# Test: Does it converge or oscillate?
tracker = UsageTracker(mode="learn")

# Run 200 turns
# Plot weight changes over time
# Validate convergence detection triggers appropriately
```

### Metrics to Validate

**Injection Rate:**
- Baseline (v1.1): ~45% (estimated)
- Target (v1.2): >75%

**Budget Utilization:**
- Baseline: 30-100% (high variance)
- Target: 70-90% (consistent)

**First-Turn Context:**
- Baseline: ~40% of needed files present
- Target: >80% of needed files present

---

## Circuit Breakers (Ralph Loop Safeguards)

### 1. Runaway Learning

```python
if iteration_count > 500:
    raise CircuitBreakerTripped("Max learning iterations exceeded")
```

### 2. Weight Instability

```python
if weight_variance > 0.5:  # Weights thrashing
    raise CircuitBreakerTripped("Weights unstable, oscillating")
```

### 3. Storage Overflow

```python
if len(usage_history) > 10000:
    archive_old_data()  # Keep last 1000, archive rest
```

### 4. Performance Degradation

```python
if tracking_overhead > 1000:  # >1s overhead
    raise CircuitBreakerTripped("Tracking too slow")
```

---

## Success Criteria

**Phase 1 Complete When:**
- ✅ Tracking correctly infers file usage from tool calls
- ✅ Statistics accurately reflect injection vs access rates
- ✅ Keyword weights adjust based on usefulness
- ✅ Convergence detection works (no infinite learning)
- ✅ Budget utilization improves >10% over baseline
- ✅ Injection rate improves >15% over baseline

**Quantitative Targets:**
- Useful injection rate: >75% (from ~45%)
- Budget utilization: 70-90% (from 30-100%)
- Convergence time: <150 turns
- Tracking overhead: <100ms per turn

---

## Next Steps

1. **Prototype `usage-tracker.py`** - Implement core tracking
2. **Test on claude-cognitive** - Dogfood immediately
3. **Measure impact** - Quantitative metrics
4. **Integrate with router** - Modify context-router-v2.py
5. **Document results** - Update V1.2_INTELLIGENCE_ROADMAP.md

---

**Status**: Design complete, ready for prototype implementation
**See**: `V1.2_INTELLIGENCE_ROADMAP.md` Phase 1 for implementation plan
**Philosophy**: Ralph Loop - iterate, measure, learn, refine
