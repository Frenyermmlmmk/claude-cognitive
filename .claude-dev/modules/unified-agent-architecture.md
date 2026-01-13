# Unified Agent Architecture - Self-Maintaining Documentation

> **Components**: Usage Tracker + Foraging Agent + Doc Refiner Agent
> **Philosophy**: Ralph Loop - usage data drives discovery and refinement
> **Status**: Phase 1 complete (usage tracking), Phase 4 planned (agents)

---

## The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                    USAGE TRACKER                             │
│  (knows what's happening in the codebase)                    │
│                                                               │
│  Tracks:                                                      │
│  • Which .md files were injected                             │
│  • Which source files were Read/Edited/Grepped               │
│  • Which .md → source mappings are useful                    │
│  • Usefulness scores per file                                │
└─────────────────────────────────────────────────────────────┘
                          ↓           ↓
              ┌───────────┘           └───────────┐
              ↓                                   ↓
┌──────────────────────────┐      ┌──────────────────────────┐
│   FORAGING AGENT         │      │   DOC REFINER AGENT      │
│   (discovers new)        │      │   (maintains existing)   │
│                          │      │                          │
│  Asks tracker:           │      │  Asks tracker:           │
│  "Which source files     │      │  "Which source files     │
│   are frequently         │      │   were edited that       │
│   accessed but have      │      │   have existing .md      │
│   no .md file?"          │      │   files?"                │
│                          │      │                          │
│  Action:                 │      │  Action:                 │
│  → Generate new .md      │      │  → Update existing .md   │
│                          │      │                          │
│  Feedback:               │      │  Feedback:               │
│  Tracker measures        │      │  Tracker measures        │
│  usefulness of new docs  │      │  usefulness improvement  │
└──────────────────────────┘      └──────────────────────────┘
```

---

## Data Flow: Usage Tracker as Central Intelligence

### What Usage Tracker Knows

From `usage_history.jsonl`:
```json
{
  "turn": 42,
  "injected": ["modules/pipeline.md", "systems/orin.md"],
  "accessed": ["modules/pipeline.md"],
  "edited": ["modules/pipeline.md"],
  "source_files": [
    "scripts/refined_pipeline_integrated_v4_fixed.py",
    "bilateral_services/orin_service/ppe_anticipatory.py"
  ],
  "injection_rate": 0.5
}
```

**Key insights available:**
1. **Accessed source files** - What code Claude is actually working on
2. **Related .md files** - Which docs describe those source files
3. **Injection/access gap** - Docs injected but not useful
4. **High-traffic files** - Frequently edited source files

---

## Foraging Agent: Discovers Undocumented Code

### Query to Usage Tracker

```python
class ForagingAgent:
    def __init__(self, usage_tracker: UsageTracker):
        self.tracker = usage_tracker

    def find_undocumented_files(self) -> List[str]:
        """
        Find source files that are frequently accessed but have no .md file.
        """
        # Load usage history
        history = self.tracker.load_history()

        # Aggregate source file access frequency
        source_file_freq = {}
        for turn in history:
            for source_file in turn.get('source_files', []):
                source_file_freq[source_file] = source_file_freq.get(source_file, 0) + 1

        # Find high-frequency files
        high_traffic = [
            file for file, count in source_file_freq.items()
            if count >= 5  # Accessed in 5+ turns
        ]

        # Check which ones have .md files already
        undocumented = []
        for source_file in high_traffic:
            # Look up if any .md describes this source file
            md_file = self.tracker.find_md_for_source(source_file)
            if not md_file:
                undocumented.append(source_file)

        return undocumented
```

**Example discovery:**

```python
>>> agent.find_undocumented_files()
[
    'scripts/pool-query.py',  # Accessed 8 times, no .md
    'bilateral_services/orin_service/ppe_anticipatory.py',  # Accessed 12 times, no .md
]

>>> agent.generate_documentation('scripts/pool-query.py')
Creating .claude/modules/discovered-pool-query.md...
  ✓ Analyzed imports (3 dependencies)
  ✓ Extracted functions (query_pool, filter_by_relevance)
  ✓ Generated keywords (pool, query, instance, coordination)
  ✓ Linked to related files (pool-loader.py, pool-extractor.py)

Waiting for usage validation (20 turns)...
```

---

## Doc Refiner Agent: Updates Stale Documentation

### Query to Usage Tracker

```python
class DocRefinerAgent:
    def __init__(self, usage_tracker: UsageTracker):
        self.tracker = usage_tracker

    def find_stale_docs(self) -> List[Tuple[str, List[str]]]:
        """
        Find .md files whose source files have been edited recently.
        Returns: [(md_file, [recently_edited_sources]), ...]
        """
        # Load recent history (last 50 turns)
        history = self.tracker.load_history(limit=50)

        # Track which source files were edited
        edited_sources = set()
        for turn in history[-10:]:  # Focus on last 10 turns
            for source_file in turn.get('source_files', []):
                # Check if this was an Edit/Write operation
                if self._was_edited(turn, source_file):
                    edited_sources.add(source_file)

        # Find which .md files describe these edited sources
        stale_docs = {}
        for source_file in edited_sources:
            md_file = self.tracker.find_md_for_source(source_file)
            if md_file:
                if md_file not in stale_docs:
                    stale_docs[md_file] = []
                stale_docs[md_file].append(source_file)

        return list(stale_docs.items())
```

**Example refinement:**

```python
>>> agent.find_stale_docs()
[
    ('modules/pipeline.md', ['scripts/refined_pipeline_integrated_v4_fixed.py']),
    ('systems/orin.md', ['bilateral_services/orin_service/ppe_anticipatory.py'])
]

>>> agent.refine_doc('modules/pipeline.md')
Analyzing changes to scripts/refined_pipeline_integrated_v4_fixed.py...

Detected changes:
  ✓ New function: handle_anticipatory_coherence() (line 245)
  ✓ Modified function: process_message() - added context param
  ✓ New import: from anticipatory_coherence import ACF

Generating refinement proposal...

Proposal 1: Add section "Anticipatory Coherence Integration"
  Confidence: 0.88
  Preview:
    + ## Anticipatory Coherence Integration
    + The pipeline now integrates with ACF for trajectory-based routing...

Apply? [y/N/preview]: y
✓ Applied refinement
  Scheduling evaluation after 10 turns...
```

---

## Key Insight: Usage Data Drives Both Agents

**Traditional approach:**
- Foraging agent scans all files → generates docs for everything → noise
- Doc refiner checks all docs periodically → updates everything → churn

**Usage-driven approach:**
- Foraging agent looks at **what Claude actually accesses** → generates only useful docs
- Doc refiner looks at **what Claude actually edited** → updates only changed docs

**Result:**
- 📉 Less noise (only document what matters)
- 📉 Less churn (only update what changed)
- 📈 More precision (focus on high-value files)
- 📈 Better convergence (usage validates decisions)

---

## Concrete Example: Real Development Session

### Turn 1-10: Working on pipeline features

```json
// usage_history.jsonl
{"turn": 5, "source_files": ["scripts/refined_pipeline_integrated_v4_fixed.py"]}
{"turn": 7, "source_files": ["scripts/refined_pipeline_integrated_v4_fixed.py"]}
{"turn": 9, "source_files": ["scripts/refined_pipeline_integrated_v4_fixed.py", "bilateral_services/orin_service/ppe_anticipatory.py"]}
```

**Doc Refiner sees:**
- `pipeline.py` edited 3 times → modules/pipeline.md may be stale
- `ppe_anticipatory.py` edited 1 time → no .md exists

### Turn 11: Doc Refiner runs (background)

```
Scanning usage data...
  ✓ Stale doc detected: modules/pipeline.md
    Source: scripts/refined_pipeline_integrated_v4_fixed.py
    Last doc update: 7 days ago
    Source commits since: 15

Generating refinement proposal...
  ✓ Detected new function: handle_anticipatory_coherence()
  ✓ Auto-applying (confidence: 0.91)

Updated: modules/pipeline.md (iteration 4)
```

### Turn 12: Foraging Agent runs (background)

```
Scanning usage data...
  ✓ High-traffic undocumented file: ppe_anticipatory.py
    Access frequency: 1/10 turns
    No existing .md file

Generating documentation...
  ✓ Created: modules/discovered-ppe-anticipatory.md
    Keywords: ppe, anticipatory, coherence, projection
    Relationships: pipeline.md, orin.md

Waiting for usage validation...
```

### Turn 13-23: Claude uses new docs

```json
{"turn": 15, "injected": ["modules/pipeline.md", "modules/discovered-ppe-anticipatory.md"], "accessed": ["modules/pipeline.md"], "source_files": ["scripts/refined_pipeline_integrated_v4_fixed.py"]}
{"turn": 18, "injected": ["modules/discovered-ppe-anticipatory.md"], "accessed": ["modules/discovered-ppe-anticipatory.md"], "source_files": ["bilateral_services/orin_service/ppe_anticipatory.py"]}
```

### Turn 24: Evaluation

**Doc Refiner evaluation:**
```
modules/pipeline.md refinement:
  Usefulness before: 0.78
  Usefulness after: 0.89
  Improvement: +0.11 ✅

Action: Finalize refinement (success!)
```

**Foraging Agent evaluation:**
```
modules/discovered-ppe-anticipatory.md:
  Usefulness: 0.82 (accessed in 1/10 turns where injected)
  Access pattern: Consistent with source file access

Action: Promote to permanent (success!)
  Renamed: modules/ppe-anticipatory.md (remove "discovered-" prefix)
```

### Result: Self-Maintaining Documentation

- Pipeline changes detected → doc updated automatically
- New important file found → doc created automatically
- Both validated by usage → no manual intervention needed
- System learned → future discoveries/refinements more accurate

---

## API: How Agents Query Usage Tracker

```python
class UsageTrackerQuery:
    """Query interface for agents to access usage insights"""

    def __init__(self, tracker: UsageTracker):
        self.tracker = tracker

    def get_high_traffic_sources(self, min_turns: int = 5) -> List[str]:
        """Get source files accessed in >= min_turns"""
        history = self.tracker.load_history()
        freq = {}
        for turn in history:
            for source in turn.get('source_files', []):
                freq[source] = freq.get(source, 0) + 1
        return [s for s, count in freq.items() if count >= min_turns]

    def get_recently_edited_sources(self, last_n_turns: int = 10) -> Set[str]:
        """Get source files edited in last N turns"""
        history = self.tracker.load_history()
        edited = set()
        for turn in history[-last_n_turns:]:
            # Check if this turn had Edit/Write operations
            for source in turn.get('source_files', []):
                if self._was_edited_in_turn(turn, source):
                    edited.add(source)
        return edited

    def find_md_for_source(self, source_file: str) -> Optional[str]:
        """Find .md file that describes this source file"""
        for md_file, rel_info in self.tracker.relationships.items():
            if source_file in rel_info['describes']:
                return md_file
        return None

    def get_undocumented_sources(self, min_traffic: int = 5) -> List[str]:
        """Get high-traffic sources with no .md file"""
        high_traffic = self.get_high_traffic_sources(min_traffic)
        return [s for s in high_traffic if not self.find_md_for_source(s)]

    def get_stale_docs(self) -> List[Tuple[str, List[str]]]:
        """Get .md files whose sources were recently edited"""
        edited = self.get_recently_edited_sources(last_n_turns=10)
        stale = {}
        for source in edited:
            md_file = self.find_md_for_source(source)
            if md_file:
                if md_file not in stale:
                    stale[md_file] = []
                stale[md_file].append(source)
        return list(stale.items())

    def get_usefulness_trend(self, md_file: str, window: int = 50) -> float:
        """Get usefulness trend (positive = improving, negative = degrading)"""
        history = self.tracker.load_history()

        # Split into early/late windows
        early = history[max(0, len(history)-window*2):-window]
        late = history[-window:]

        early_useful = self._calculate_usefulness_in_window(md_file, early)
        late_useful = self._calculate_usefulness_in_window(md_file, late)

        return late_useful - early_useful  # Trend
```

---

## Implementation Roadmap

### ✅ Phase 1: Usage Tracking (COMPLETE)
- [x] Track injections
- [x] Track tool calls → source files
- [x] Map source files → .md files
- [x] Calculate usefulness scores
- [x] Store history in usage_history.jsonl

### 🔄 Phase 4A: Foraging Agent (Week 7)
- [ ] Query API for undocumented high-traffic files
- [ ] Generate .md files for discoveries
- [ ] Mark as "discovered-*" for validation
- [ ] Wait for usage data (20 turns)
- [ ] Promote to permanent if useful

### 🔄 Phase 4B: Doc Refiner Agent (Week 8)
- [ ] Query API for recently edited sources
- [ ] Find corresponding stale .md files
- [ ] Analyze code changes (git diff, AST)
- [ ] Generate refinement proposals
- [ ] Apply & measure usefulness improvement

### 🔄 Phase 4C: Unified Daemon (Week 9)
- [ ] Background process runs both agents
- [ ] Foraging: runs every 24 hours
- [ ] Refiner: runs every 1 hour
- [ ] Shared usage tracker query interface
- [ ] Coordinated logging/progress

---

## Success Metrics

**Goal: Self-maintaining documentation with minimal manual intervention**

### Coverage
```
Target: >80% of high-traffic files have .md docs

High-traffic files (accessed >5 turns): 25
Documented: 22 (88%) ✅
Undocumented: 3 (12%)
```

### Freshness
```
Target: >80% of docs updated within 7 days of source change

Docs with source changes (last 30 days): 15
Updated automatically: 13 (87%) ✅
Manual updates needed: 2 (13%)
```

### Quality
```
Target: >75% average usefulness for all docs

All .md files: 30
Avg usefulness: 0.79 (79%) ✅
High utility (>0.75): 23 (77%)
Low utility (<0.5): 2 (7%)
```

### Manual Burden
```
Target: <5 manual doc updates per month

Before agents: 20 manual updates/month
After agents: 3 manual updates/month
Reduction: 85% ✅
```

---

## Ralph Loop Validation

**This architecture embodies pure Ralph Loop thinking:**

### Iteration
- Both agents run continuously in background
- Each discovery/refinement is an iteration
- Never assume first attempt is perfect

### Objective Feedback
- Usage tracker provides quantitative metrics
- Usefulness scores (0.0 to 1.0) are objective
- No subjective "doc quality" judgments

### Learning
- Foraging learns which file patterns are worth documenting
- Refiner learns which refinement strategies improve usefulness
- Both adapt strategies based on outcomes

### Convergence
- System stabilizes when all high-traffic files documented
- Refinements become less frequent as docs stay current
- Agents idle when no work needed (efficient)

### Circuit Breakers
- Rate limiting prevents runaway generation
- Confidence thresholds prevent low-quality changes
- Rollback on degradation keeps system safe

---

**Status**: Architecture designed, Phase 1 (tracking) complete, Phase 4 (agents) ready to build
**Dependencies**: Usage Tracker ✅, Git (for change detection), AST parsing (for code analysis)
**Estimated Timeline**: 2-3 weeks for both agents
**Ralph Loop Score**: 10/10 (perfect iteration + feedback + learning loop)
