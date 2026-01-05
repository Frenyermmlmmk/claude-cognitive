# Claude Cognitive

> Working memory for Claude Code — persistent context and multi-instance coordination

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production](https://img.shields.io/badge/Status-Production-green.svg)]()

---

## The Problem

Claude Code is powerful but stateless. Every new instance:
- **Rediscovers** your codebase from scratch
- **Hallucinates** integrations that don't exist
- **Repeats** debugging you already tried
- **Burns tokens** re-reading unchanged files

With large codebases (50k+ lines), this becomes painful fast.

---

## The Solution

**Claude Cognitive** gives Claude Code working memory through two complementary systems:

### 1. Context Router
**Attention-based file injection** with cognitive dynamics:
- **HOT** (>0.8): Full file injection - active development
- **WARM** (0.25-0.8): Headers only - background awareness
- **COLD** (<0.25): Evicted from context

Files **decay** when not mentioned, **activate** on keywords, and **co-activate** with related files.

### 2. Pool Coordinator
**Multi-instance state sharing** for long-running sessions:
- **Automatic mode**: Detects completions/blockers from conversation (every 5min)
- **Manual mode**: Explicit `pool` blocks for critical coordination
- Works with persistent sessions (days/weeks), not just short bursts

---

## Results

**Token Savings:**
- Cold start: **79%** (120K → 25K chars)
- Warm context: **70%** (80K → 24K chars)
- Focused work: **75%** (60K → 15K chars)

**Average: 64-95% depending on codebase size and work pattern.**

**Developer Experience:**
- ✅ New instances productive in **first message**
- ✅ Zero hallucinated imports/integrations
- ✅ No duplicate work across 8+ concurrent instances
- ✅ Persistent memory across days-long sessions

**Validated on:**
- 1+ million line production codebase (3,200+ Python modules)
- 4-node distributed architecture
- 8 concurrent Claude Code instances
- Multi-day persistent sessions

---

## Quick Start

### 1. Install Scripts

```bash
# Clone to your home directory
cd ~
git clone https://github.com/GMaN1911/claude-cognitive.git .claude-cognitive

# Copy scripts
cp -r .claude-cognitive/scripts ~/.claude/scripts/

# Set up hooks (adds to existing config)
cat .claude-cognitive/hooks-config.json >> ~/.claude/settings.json
```

### 2. Initialize Your Project

```bash
cd /path/to/your/project

# Create .claude directory
mkdir -p .claude/{systems,modules,integrations,pool}

# Copy templates
cp -r ~/.claude-cognitive/templates/* .claude/

# Edit .claude/CLAUDE.md with your project info
# Edit .claude/systems/*.md to describe your architecture
```

### 3. Set Instance ID

```bash
# Add to ~/.bashrc for persistence:
export CLAUDE_INSTANCE=A

# Or per-terminal:
export CLAUDE_INSTANCE=B
```

### 4. Verify It's Working

```bash
# Start Claude Code
claude

# First message - check for context injection:
# Should see: "ATTENTION STATE [Turn 1]" with HOT/WARM/COLD counts

# Query pool activity:
python3 ~/.claude/scripts/pool-query.py --since 1h
```

### 5. Customize Keywords (Optional, Recommended)

**The scripts work immediately with MirrorBot example keywords** (50-70% savings).

**For 80-95% savings:** Customize keywords to match your codebase.

**Quick customization:**
```bash
# Edit the keyword section
nano ~/.claude/scripts/context-router-v2.py

# See full guide:
cat ~/.claude-cognitive/CUSTOMIZATION.md
```

**Full setup guide:** [SETUP.md](./SETUP.md)
**Customization guide:** [CUSTOMIZATION.md](./CUSTOMIZATION.md)

---

## How It Works

### Context Router

**Attention Dynamics:**
```
User mentions "orin" in message
    ↓
systems/orin.md → score = 1.0 (HOT)
    ↓
Co-activation:
  integrations/pipe-to-orin.md → +0.35 (WARM)
  modules/t3-telos.md → +0.35 (WARM)
    ↓
Next turn (no mention):
  systems/orin.md → 1.0 × 0.85 decay = 0.85 (still HOT)
    ↓
3 turns later (no mention):
  systems/orin.md → 0.85 × 0.85 × 0.85 = 0.61 (now WARM)
```

**Injection:**
- HOT files: Full content injected
- WARM files: First 25 lines (headers) injected
- COLD files: Not injected (evicted)

### Pool Coordinator

**Automatic Mode:**
```
Instance A completes task
    ↓
Auto-detector finds: "Successfully deployed PPE to Orin"
    ↓
Writes pool entry:
  action: completed
  topic: PPE deployment to Orin
  affects: orin_sensory_cortex/
    ↓
Instance B starts session
    ↓
Pool loader shows:
  "[A] completed: PPE deployment to Orin"
    ↓
Instance B avoids duplicate work
```

**Manual Mode:**
````markdown
```pool
INSTANCE: A
ACTION: completed
TOPIC: Fixed authentication bug
SUMMARY: Resolved race condition in token refresh. Added mutex.
AFFECTS: auth.py, session_handler.py
BLOCKS: Session management refactor can proceed
```
````

---

## History Tracking (v1.1+)

**Claude Cognitive now remembers its own attention.** Every turn is logged with structured data showing which files were HOT/WARM/COLD and how they transitioned between tiers.

### Why This Matters

The router always computed attention scores. Now they persist as queryable history:
- **Replay development trajectories** - "How did we stabilize the PPE last week?"
- **Identify neglected modules** - "Which files got ignored during the sprint?"
- **Debug attention behavior** - "Why didn't convergent.md activate when I mentioned convergence?"

### View History

```bash
# Last 20 turns
python3 ~/.claude/scripts/history.py

# Last 2 hours
python3 ~/.claude/scripts/history.py --since 2h

# Filter by file pattern
python3 ~/.claude/scripts/history.py --file ppe

# Show only tier transitions
python3 ~/.claude/scripts/history.py --transitions

# Summary statistics
python3 ~/.claude/scripts/history.py --stats

# Filter by instance
python3 ~/.claude/scripts/history.py --instance A
```

### Example Output

```
============================================================
  2025-12-31
============================================================

[18:43:21] Instance A | Turn 47
  Query: refactor ppe routing tier collapse
  🔥 HOT: ppe-anticipatory-coherence.md, t3-telos.md
  🌡️  WARM: orin.md, pipeline.md
  ⬆️  Promoted to HOT: ppe-anticipatory-coherence.md
  ⬇️  Decayed to COLD: img-to-asus.md

[19:22:35] Instance A | Turn 48
  Query: what divergence dynamics?
  🔥 HOT: divergent.md, t3-telos.md, cvmp-transformer.md
  🌡️  WARM: pipeline.md, orin.md (+3 more)
  ⬆️  Promoted to HOT: divergent.md
```

### Statistics View

```bash
python3 ~/.claude/scripts/history.py --stats --since 7d
```

```
╔══════════════════════════════════════════════════════════════╗
║                    ATTENTION STATISTICS                      ║
╚══════════════════════════════════════════════════════════════╝

Total turns: 342
Time range: 2025-12-24 to 2025-12-31

Instances: {'A': 156, 'B': 98, 'default': 88}

Most frequently HOT:
   87 turns: pipeline.md
   65 turns: t3-telos.md
   43 turns: orin.md
   38 turns: ppe-anticipatory-coherence.md
   22 turns: divergent.md

Most promoted to HOT:
   23 times: ppe-anticipatory-coherence.md
   18 times: divergent.md
   12 times: convergent.md

Busiest days:
  2025-12-30: 156 turns
  2025-12-29: 98 turns
  2025-12-28: 88 turns

Average context size: 18,420 chars
```

### History Entry Structure

Each turn logs:
```json
{
  "turn": 47,
  "timestamp": "2025-12-31T18:43:21Z",
  "instance_id": "A",
  "prompt_keywords": ["refactor", "ppe", "routing", "tier"],
  "activated": ["ppe-anticipatory-coherence.md"],
  "hot": ["ppe-anticipatory-coherence.md", "t3-telos.md"],
  "warm": ["orin.md", "pipeline.md"],
  "cold_count": 12,
  "transitions": {
    "to_hot": ["ppe-anticipatory-coherence.md"],
    "to_warm": ["orin.md"],
    "to_cold": ["img-to-asus.md"]
  },
  "total_chars": 18420
}
```

**File:** `~/.claude/attention_history.jsonl` (append-only, one entry per turn)

**Retention:** 30 days (configurable in `context-router-v2.py`)

---

## Architecture

```
claude-cognitive/
├── scripts/
│   ├── context-router-v2.py      # Attention dynamics + history logging
│   ├── history.py                # History viewer CLI (v1.1+)
│   ├── pool-auto-update.py       # Continuous pool updates
│   ├── pool-loader.py            # SessionStart injection
│   ├── pool-extractor.py         # Stop hook extraction
│   └── pool-query.py             # CLI query tool
│
├── templates/
│   ├── CLAUDE.md                 # Project context template
│   ├── systems/                  # Hardware/deployment
│   ├── modules/                  # Core systems
│   └── integrations/             # Cross-system communication
│
└── examples/
    ├── small-project/            # Simple example
    ├── monorepo/                 # Complex structure
    └── mirrorbot-sanitized/      # Real-world 50k+ line example
```

**Hooks:**
- `UserPromptSubmit`: Context router + pool auto-update
- `SessionStart`: Pool loader
- `Stop`: Pool extractor (manual blocks)

**State Files:**
- `.claude/attn_state.json` - Context router scores
- `.claude/pool/instance_state.jsonl` - Pool entries

**Strategy:** Project-local first, `~/.claude/` fallback (monorepo-friendly)

---

## Documentation

### Concepts
- [Attention Decay](./docs/concepts/attention-decay.md) - Why files fade
- [Context Tiers](./docs/concepts/context-tiers.md) - HOT/WARM/COLD theory
- [Pool Coordination](./docs/concepts/pool-coordination.md) - Multi-instance patterns
- [Fractal Documentation](./docs/concepts/fractal-docs.md) - Infinite zoom strategy

### Guides
- [Getting Started](./docs/guides/getting-started.md) - First 15 minutes
- [Large Codebases](./docs/guides/large-codebases.md) - 50k+ lines
- [Team Setup](./docs/guides/team-setup.md) - Multiple developers
- [Migration](./docs/guides/migration.md) - Adding to existing project

### Reference
- [Template Syntax](./docs/reference/template-syntax.md) - Markers and tags
- [Pool Protocol](./docs/reference/pool-protocol.md) - Technical spec
- [Token Budgets](./docs/reference/token-budgets.md) - Optimization guide

---

## Use Cases

### Solo Developer - Large Codebase
**Problem:** 50k+ line Python project, Claude forgets architecture between sessions

**Solution:**
- Context router keeps architecture docs HOT when mentioned
- Token usage drops 79% (120K → 25K chars)
- New sessions productive immediately

### Team - Monorepo
**Problem:** 4 developers, each running Claude in different terminals, duplicate work

**Solution:**
- Each dev sets `CLAUDE_INSTANCE=A/B/C/D`
- Pool coordinator shares completions/blockers
- Zero duplicate debugging

### Long-Running Sessions
**Problem:** Keep Claude open for days, it forgets what happened 2 days ago

**Solution:**
- Pool auto-updates write history continuously
- Context router maintains attention across days
- Temporal coherence preserved

---

## Enterprise

Need multi-team coordination, compliance features, or custom setup?

**Contact:** gsutherland@mirrorethic.com

**Services available:**
- Custom implementation for your codebase
- Team training and onboarding
- Integration with existing tooling
- Priority support and SLA

---

## Roadmap

**v1.1 (Current - Production)**
- ✅ Context router with attention dynamics
- ✅ Pool coordinator (auto + manual)
- ✅ Project-local strategy
- ✅ CLI query tools
- ✅ **Attention history tracking** (NEW in v1.1)
- ✅ **History viewer CLI** (NEW in v1.1)

**v1.2 (Next)**
- [ ] Graph visualization of attention flow
- [ ] Collision detection (multiple instances, same file HOT)
- [ ] Nemotron compression for pool summaries
- [ ] Semantic relevance (embeddings vs keywords)

**v2.0 (Future)**
- [ ] Conflict detection (multiple instances, same file)
- [ ] Action confirmations (critical operations)
- [ ] Integration with ES-AC learning (context preferences)
- [ ] Oracle prediction (which files to pre-load)
- [ ] Exploring integration with other AI coding assistants (Gemini CLI, Cursor, Aider)

---

## Credits

**Built on production experience with:**
- 1+ million lines of production Python code across 3,200+ modules
- 4-node distributed architecture (Legion, Orin, ASUS, Pi5)
- 8+ concurrent Claude Code instances in daily use

**Created by:**
- Garret Sutherland, [MirrorEthic LLC](https://mirrorethic.com)


---

## License

MIT License - see [LICENSE](./LICENSE)

**Use it, modify it, ship it.**

---

## Contributing

Issues and PRs welcome!

**Before submitting:**
1. Check [existing issues](https://github.com/GMaN1911/claude-cognitive/issues)
2. For features: Open issue first to discuss
3. For bugs: Include context router + pool logs

**Development:**
```bash
# Test locally
cd ~/your-project
export CLAUDE_INSTANCE=TEST
claude

# Check logs
tail -f ~/.claude/context_injection.log
python3 ~/.claude/scripts/pool-query.py --since 10m
```

---

**Questions?** Open an [issue](https://github.com/GMaN1911/claude-cognitive/issues)

**Updates?** Watch the [repo](https://github.com/GMaN1911/claude-cognitive) for releases


