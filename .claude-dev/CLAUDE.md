# claude-cognitive Development (Project-Local Context)

> **Project**: claude-cognitive v1.2 Intelligence Enhancement
> **Purpose**: Dogfooding - use claude-cognitive to build claude-cognitive
> **Status**: v1.1 Production (global ~/.claude/), v1.2 Development (this project)

---

## Current Work

**Phase**: v1.2 Planning + Initial Prototyping
**Focus**: Ralph Loop integration + Phase 1 (Usage Tracking)

**Recent Activity**:
- ✅ Created V1.2_INTELLIGENCE_ROADMAP.md (comprehensive plan)
- ✅ Created RALPH_LOOP_INSIGHTS.md (philosophical foundation)
- ✅ Integrated Ralph Loop pattern into roadmap
- 🔄 Setting up project-local .claude-dev/ for dogfooding (development only)
- ⏭️ Next: Prototype usage-tracker.py

---

## Project Structure

```
claude-cognitive-package/
├── scripts/                          # v1.1 production scripts (copy to ~/.claude/scripts/)
│   ├── context-router-v2.py         # [v1.1] Core router (INSTALLED GLOBALLY)
│   ├── history.py                   # [v1.1] History viewer (INSTALLED GLOBALLY)
│   ├── pool-*.py                    # [v1.1] Pool coordination (INSTALLED GLOBALLY)
│   │
│   ├── usage-tracker.py             # [v1.2] PROTOTYPE - Usage learning
│   ├── semantic-matcher.py          # [v1.2] PROTOTYPE - Fuzzy matching
│   ├── predictor.py                 # [v1.2] PROTOTYPE - Sequence learning
│   └── forage.py                    # [v1.2] PROTOTYPE - Ralph Loop foraging
│
├── .claude-dev/                      # DEV-ONLY context (dogfooding, NOT for users)
│   ├── CLAUDE.md                    # This file
│   ├── modules/                     # claude-cognitive components
│   │   ├── context-router.md        # Router internals
│   │   ├── pool-coordinator.md      # Pool system
│   │   ├── usage-tracker.md         # v1.2 usage learning
│   │   └── foraging-agent.md        # v1.2 Ralph Loop agent
│   └── integrations/
│       └── claude-code-hooks.md     # Hook integration points
│
├── V1.2_INTELLIGENCE_ROADMAP.md     # Master plan
├── RALPH_LOOP_INSIGHTS.md           # Philosophy
├── README.md                        # Public-facing docs
└── templates/                       # User templates
```

---

## Keywords (Project-Specific)

**v1.2 Development**:
- usage, tracking, learning, feedback, ralph, loop, iteration
- foraging, discovery, autonomous, agent, convergence
- semantic, embedding, similarity, matching
- prediction, sequence, pre-loading, anticipatory
- budget, adaptive, threshold, dynamic
- circuit-breaker, safeguard, protection

**Core Components** (v1.1):
- router, context, attention, activation, decay
- keyword, injection, hot, warm, cold
- history, pool, coordinator, instance

**Files/Modules**:
- context-router-v2, usage-tracker, foraging-agent
- semantic-matcher, predictor, history

---

## When Working On...

### **Usage Tracking (Phase 1)**
Auto-activates:
- `.claude-dev/modules/usage-tracker.md`
- `.claude-dev/modules/context-router.md` (integration points)

### **Foraging Agent (Phase 4)**
Auto-activates:
- `.claude-dev/modules/foraging-agent.md`
- `RALPH_LOOP_INSIGHTS.md`
- `.claude-dev/modules/usage-tracker.md` (feedback loop)

### **Semantic Matching (Phase 2)**
Auto-activates:
- `.claude-dev/modules/semantic-matcher.md`
- `.claude-dev/modules/context-router.md`

### **Pool System**
Auto-activates:
- `.claude-dev/modules/pool-coordinator.md`
- `.claude-dev/integrations/claude-code-hooks.md`

---

## Development Workflow

### Prototyping (Current Phase)

**1. Create Prototype:**
```bash
# Phase 1: Usage tracking
touch scripts/usage-tracker.py
# Write prototype with _prototype suffix during development
```

**2. Test on This Project:**
```bash
# Dogfood immediately
cd /home/garret-sutherland/claude-cognitive-package/
python scripts/usage-tracker.py --test

# Check if it tracks attention state correctly
cat .claude-dev/attn_state.json
```

**3. Measure Impact:**
```bash
# Before: Baseline context quality
# After: Context quality with usage tracking
# Document results in V1.2_INTELLIGENCE_ROADMAP.md
```

**4. Integrate:**
```bash
# Once validated, integrate into context-router-v2.py
# Or keep standalone if appropriate
```

### Testing Strategy

**Test Environments:**
1. **This project** (claude-cognitive itself) - Primary dogfooding
2. **Small example project** - Validate zero-config experience
3. **Large project** (if available) - Validate scalability

**Metrics to Track:**
- Token savings (% reduction)
- First-turn context quality (% of needed files available)
- Wasted context (% of injected files unused)
- Time to productivity (seconds until first useful action)

---

## Critical Principles

### 1. **Dogfooding is Mandatory**
- Every v1.2 feature tested on claude-cognitive itself first
- Attention state visible while developing
- Use pool coordination for multi-session work

### 2. **Ralph Loop Philosophy**
- Iteration > perfection
- Objective feedback required
- Convergence detection prevents waste
- Circuit breakers prevent disasters

### 3. **Backwards Compatibility**
- v1.1 users upgrade seamlessly
- No breaking changes to core router
- New features opt-in or auto-enabled safely

### 4. **Quantitative Validation**
- Every feature needs metrics
- Measure on 3+ projects before merging
- Document results in roadmap

---

## Quick Reference

**Main Docs**:
- `V1.2_INTELLIGENCE_ROADMAP.md` - Master plan
- `RALPH_LOOP_INSIGHTS.md` - Philosophy
- `README.md` - Public docs
- `CHANGELOG.md` - Version history

**Context Docs** (Development):
- `.claude-dev/modules/context-router.md` - Router internals
- `.claude-dev/modules/usage-tracker.md` - Usage learning (v1.2)
- `.claude-dev/modules/foraging-agent.md` - Ralph Loop agent (v1.2)
- `.claude-dev/modules/pool-coordinator.md` - Pool system

**Global Installation**:
- `~/.claude/scripts/` - v1.1 production scripts (LIVE)
- `~/.claude/attention_history.jsonl` - Active history log
- `~/.claude/attn_state.json` - Current attention scores

---

## Next Steps

**Immediate (Today)**:
1. Create `.claude-dev/modules/*.md` files for v1.2 components
2. Start prototyping `usage-tracker.py`
3. Test on this project (dogfood)

**Short-term (This Week)**:
1. Complete Phase 1 prototypes (usage tracking + explanations)
2. Measure impact quantitatively
3. Document results in roadmap

**Medium-term (Next 2 Weeks)**:
1. Phase 2: Semantic matching + dynamic budgeting
2. Integration testing on multiple projects
3. Community feedback (GitHub discussions)

---

**Working on v1.2?** Check current phase in `V1.2_INTELLIGENCE_ROADMAP.md`
**Need context?** Mention keywords above to activate relevant modules
**Testing?** Always dogfood on this project first
