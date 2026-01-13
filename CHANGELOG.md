# Changelog

All notable changes to claude-cognitive will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.2.1] - 2026-01-12

### 🐛 Bug Fixes

#### Critical: docs_root Resolution Priority Bug (Issue #9)
**Problem**: Users seeing wrong documentation files (global ~/.claude/ instead of project-local .claude/)

**Root Cause**: `context-router-v2.py` was not checking project-local `.claude/` directory, only:
1. CONTEXT_DOCS_ROOT env var
2. Global ~/.claude/ (fallback)

This caused users to load documentation from the global directory (which may contain unrelated project docs) instead of their project-specific documentation.

**Fix**: Implemented proper 3-tier priority order:
1. **CONTEXT_DOCS_ROOT environment variable** (explicit override)
2. **Project-local .claude/ directory** (if exists with .md files) ← **NEW**
3. **Global ~/.claude/ directory** (fallback)

**Impact**:
- ✅ Project-local docs now correctly take priority over global
- ✅ Explicit validation: Checks for .md files, not just directory existence
- ✅ Helpful error messages if no docs found
- ✅ Debug output shows which docs_root was chosen

**User Action Required**: None - automatic fix
- If you were using `export CONTEXT_DOCS_ROOT=.claude` workaround, you can now remove it
- Project-local `.claude/` will be automatically detected

**Files Modified**:
- `scripts/context-router-v2.py`: Added `resolve_docs_root()` function with proper priority logic

### 📝 Changes

#### Added
- `resolve_docs_root()` function with explicit priority order
- Content validation (checks for .md files, not just directory existence)
- Debug output to stderr showing which docs_root was chosen
- Helpful error message if no documentation found

#### Fixed
- Project-local .claude/ now correctly prioritized over global ~/.claude/
- Prevents accidental loading of wrong project's documentation
- Fixes Issue #9 (users seeing MirrorBot CVMP docs instead of their own)

---

## [1.2.0] - 2026-01-12 (Phase 1 Complete - Usage Tracking)

✅ **Phase 1 of v1.2 Intelligence Roadmap is complete**

### Added
- **Usage Tracking System** (Production Ready):
  - Complete observation and learning infrastructure
  - File access monitoring with Ralph Loop pattern
  - Usefulness score calculation (0.0 to 1.0)
  - Auto-adjusts keyword weights after 50 turns
  - Integration with context-router-v2.py

### Status
- ✅ Phase 1 (Usage Tracking): Complete
- 🔄 Phase 2 (Embeddings): Skipped - Moving to hologram-based discovery
- 🔜 Phase 3 (Intelligent Agents): Planned for v2.x
- 🔜 Phase 4 (Self-Learning): Planned for v2.x with hologram integration

### Next
- v2.0 introduces hologram-cognitive integration with auto-discovered DAG relationships
- Breaking change: Moves away from manual keywords.json to automatic discovery
- See v2.0 branch for hologram integration

---

## [1.1.2] - 2026-01-08 (Development Preview)

⚠️ **This is a development preview release** - v1.2 Phase 1 features are experimental

### Added - v1.2 Development (Experimental)
- **Usage Tracking System** (⚠️ Preview/Observation Mode):
  - `scripts/usage_tracker.py` - Core tracking logic with Ralph Loop learning pattern
  - `scripts/usage-track-stop.py` - Stop hook integration for post-turn analysis
  - `scripts/add-usage-tracking-hook.py` - Hook installer utility
  - Tracks which `.claude/*.md` files are injected vs actually used
  - Maps documentation to source code relationships
  - Calculates usefulness scores (0.0 to 1.0) per file
  - Auto-adjusts keyword weights after 50 turns (learning mode)
  - Generates: `.claude/usage_stats.json`, `.claude/usage_history.jsonl`, `.claude/keyword_weights.json`

- **v1.2 Architecture Documentation** (4000+ lines):
  - `V1.2_INTELLIGENCE_ROADMAP.md` - Complete 4-phase roadmap
  - `RALPH_LOOP_INSIGHTS.md` - Design philosophy (700+ lines)
  - `.claude/modules/usage-tracker.md` - Tracking system design (850+ lines)
  - `.claude/modules/foraging-agent.md` - Discovery agent design (900+ lines)
  - `.claude/modules/doc-refiner-agent.md` - Maintenance agent design (700+ lines)
  - `.claude/modules/unified-agent-architecture.md` - Combined architecture (500+ lines)
  - `V1.2_PHASE1_PROGRESS.md` - Phase 1 progress report
  - `INTEGRATION_PROGRESS.md` - Integration status and metrics
  - `SESSION_SUMMARY.md` - Latest development session notes

### Changed - v1.2 Integration
- **`scripts/context-router-v2.py`**:
  - Added usage tracker integration (injection logging)
  - Added learned keyword weight loading from `.claude/keyword_weights.json`
  - Applies learned weights during attention calculation
  - Graceful fallback if tracker unavailable
- **`~/.claude/settings.json`** (via installer):
  - Added `usage-track-stop.py` to Stop hooks array
  - Runs automatically after each conversation turn

### Added - v1.1.2 Stable Features
- **Project-local keyword configuration**: Keywords, co-activation, and pinned files now load from `.claude/keywords.json` instead of being hardcoded in the script
  - Config lookup order: project `.claude/keywords.json` > global `~/.claude/keywords.json` > empty defaults
  - Added `load_project_config()` function in `context-router-v2.py`
  - Added `templates/keywords.json.example` template file
  - Added example `keywords.json` to small-project example

### Changed - v1.1.2 Stable Features
- **docs_root resolution**: Now prefers project-local `.claude/` directory over global `~/.claude/`
  - Priority: `CONTEXT_DOCS_ROOT` env > project `.claude/` > global `~/.claude/`
- Updated all documentation to reference `.claude/keywords.json` instead of editing the Python script
  - `CUSTOMIZATION.md`: Complete rewrite for JSON config
  - `README.md`: Updated Quick Start step 5 and added Project Configuration section
  - `SETUP.md`: Added "Create Keywords Config" step
  - `docs/guides/getting-started.md`: Updated customization instructions
  - `docs/concepts/attention-decay.md`: Updated pinned files and troubleshooting sections

### Removed
- Hardcoded MirrorBot-specific keywords, co-activation rules, and pinned files from `context-router-v2.py` (~220 lines)

### Experimental
All usage tracking features are marked as experimental/preview:
- Infrastructure is complete and functional
- Currently in observation/data collection phase
- Learning mode activates automatically after 50 turns
- Validation pending with real usage data
- Can be disabled by removing stop hook

### Design Philosophy: Ralph Loop
This release embodies the **Ralph Loop pattern**: Iterate → Measure → Learn → Refine → Repeat
- Build foundation, observe real usage, learn from data, iterate
- Not "design perfect system then implement"
- Adaptive intelligence through iteration, not one-shot optimization

---

## [1.1.1] - 2026-01-02

### Fixed
- **Pool loader hardcoded fallback** (#2): Replaced hardcoded "MirrorBot/CVMP" fallback in `pool-loader.py` with dynamic project name detection
  - Added `get_project_name()` function that detects project from:
    1. Git remote URL (extracts repo name from origin)
    2. Git repository root directory name
    3. Current working directory name
    4. Generic fallback: "Current Project"
  - SessionStart hook now shows actual project name instead of misleading example data
  - Thanks to @sbozh for reporting!

---

## [1.1.0] - 2025-12-31

### Added
- **Attention History Tracking**: Every turn now logs structured attention state to `~/.claude/attention_history.jsonl`
  - Turn-by-turn record of which files were HOT/WARM/COLD
  - Tracks transitions between tiers (what got promoted, what decayed)
  - Captures prompt keywords and activated files
  - Records total context size per turn
  - 30-day retention (configurable)

- **History CLI** (`scripts/history.py`): Query and view attention trajectory over time
  - Filter by time window (`--since 2h`, `--since 1d`)
  - Filter by instance ID (`--instance A`)
  - Filter by file pattern (`--file ppe`)
  - Show only transitions (`--transitions`)
  - Summary statistics (`--stats`)
  - JSON output (`--format json`)
  - Last N entries (`--last 20` default)

- **Fractal Documentation Support**: Nested file routing for hierarchical zoom
  - Added support for `modules/t3-telos/trajectories/convergent.md` pattern
  - Parent files co-activate children on mention
  - Child files co-activate parent for context
  - Enables "zoom in" to specific details while maintaining overview

- **Documentation**:
  - Comprehensive [Fractal Documentation](./docs/concepts/fractal-docs.md) conceptual guide
  - Added History Tracking section to README
  - Updated Architecture diagram to include history.py
  - Updated Roadmap to reflect v1.1 as current

### Changed
- `context-router-v2.py`: Now persists turn-by-turn attention state with transitions
  - Added `compute_transitions()` to track tier changes
  - Added `append_history()` to log structured data
  - Deep copy state before mutation for accurate diff tracking
  - Fail-safe error handling (history write errors don't block hook)

### Why This Matters
The router always knew which files were HOT/WARM/COLD. Now that knowledge persists, letting you answer questions like:
- "What path did we take to stabilize PPE last week?"
- "Which modules got neglected during the anticipatory coherence sprint?"
- "Show me attention flow around t3-telos since Dec 25"

**Launch Metrics (48 hours):**
- 33,000+ Reddit views
- #1 post on r/claudecode
- #18 on Hacker News
- 80+ GitHub stars
- 6 forks
- Active Discord engagement with beta users

---

## [1.0.0] - 2025-12-30

### Added
- **Context Router v2.0**: Attention-based file injection with HOT/WARM/COLD tiers
  - Keyword activation (instant HOT on mention)
  - Attention decay (files fade when not mentioned)
  - Co-activation (related files boost together)
  - Token budget enforcement (25K char ceiling)
  - Project-local first, global fallback strategy

- **Pool Coordinator v2.0**: Multi-instance state sharing
  - Automatic mode: Continuous updates (detects completions/blockers from conversation)
  - Manual mode: Explicit `pool` blocks for critical coordination
  - Works with persistent sessions (days/weeks long)
  - Project-local strategy (matches context router)
  - 5-minute cooldown on auto-updates

- **Complete Documentation**:
  - README.md with comprehensive overview
  - SETUP.md with 15-minute quickstart
  - Template files for CLAUDE.md, systems, modules, integrations
  - Complete simple-project example with documentation

- **CLI Tools**:
  - `pool-query.py`: Query and filter pool entries
  - Context injection logging for debugging
  - Health check validation

- **Production Validation**:
  - Tested on 50,000+ line codebase
  - Validated with 8 concurrent instances
  - 64-95% token savings measured
  - Multi-day persistent session support

### Fixed
- Pool system workflow mismatch (designed for short sessions, now supports persistent)
- Project-local vs global state file inconsistency
- Instance ID handling in pool relevance scoring

### Technical Details
- Python 3.8+ compatible
- No external dependencies for core scripts
- Hook-based integration with Claude Code
- JSONL state persistence
- Fail-safe error handling (never blocks conversation)

---

## Development Milestones

### Phase 0: Pre-Launch Prep (Dec 30, 2025)
- ✅ Name selected: `claude-cognitive`
- ✅ License chosen: MIT
- ✅ Brand assets created (pitch, description)
- ✅ Infrastructure validated on production system

### Phase 1: Packaging (Dec 30, 2025 - In Progress)
- ✅ Repository structure created
- ✅ Core scripts extracted and documented
- ✅ Templates created
- ✅ Simple example built
- ✅ SETUP.md quickstart written
- ✅ README.md comprehensive guide written
- ⏸️ Additional examples (monorepo, MirrorBot-sanitized)
- ⏸️ Concept/guide/reference documentation

### Phase 2: Private Beta (Planned)
- Find 3-5 beta testers
- Collect feedback on setup flow
- Iterate on documentation
- Gather testimonials

### Phase 3: Public Launch (Planned)
- GitHub public release
- Hacker News "Show HN" post
- Reddit r/ClaudeAI, r/LocalLLaMA
- Twitter/X thread
- Dev.to blog post

---

## Production Usage

**MirrorBot/CVMP (Origin System):**
- 80,000+ interactions processed
- 1+ million line production codebase (3,200+ Python modules)
- 4-node distributed architecture (Legion, Orin, ASUS, Pi5)
- 8+ concurrent Claude Code instances
- Multi-day persistent sessions

**Token Savings Measured:**
- Cold start: 79% (120K → 25K chars)
- Warm context: 70% (80K → 24K chars)
- Focused work: 75% (60K → 15K chars)

---

## Credits

**Created by:** Garret Sutherland, MirrorEthic LLC

**Built on production experience with:**
- MirrorBot/CVMP consciousness modeling system
- 80,000+ real-world interactions
- Multi-instance developer workflows
- Large-scale codebase management

**Funded with instructions:** "Use it for love"

---

## License

MIT License - Copyright (c) 2025 Garret Sutherland, MirrorEthic LLC

See [LICENSE](./LICENSE) for full text.

---

[Unreleased]: https://github.com/GMaN1911/claude-cognitive/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/GMaN1911/claude-cognitive/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/GMaN1911/claude-cognitive/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/GMaN1911/claude-cognitive/releases/tag/v1.0.0
