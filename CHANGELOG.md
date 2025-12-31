# Changelog

All notable changes to claude-cognitive will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

*Nothing yet - stay tuned for v1.2!*

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

[Unreleased]: https://github.com/GMaN1911/claude-cognitive/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/GMaN1911/claude-cognitive/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/GMaN1911/claude-cognitive/releases/tag/v1.0.0
