# Changelog

All notable changes to claude-cognitive will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Concept documentation (attention decay, context tiers, pool coordination)
- Guide documentation (large codebases, team setup, migration)
- Reference documentation (template syntax, pool protocol, token budgets)
- Monorepo example
- Sanitized MirrorBot production example

---

## [1.0.0] - 2024-12-30

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

### Phase 0: Pre-Launch Prep (Dec 30, 2024)
- ✅ Name selected: `claude-cognitive`
- ✅ License chosen: MIT
- ✅ Brand assets created (pitch, description)
- ✅ Infrastructure validated on production system

### Phase 1: Packaging (Dec 30, 2024 - In Progress)
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

MIT License - Copyright (c) 2024 Garret Sutherland, MirrorEthic LLC

See [LICENSE](./LICENSE) for full text.

---

[Unreleased]: https://github.com/GMaN1911/claude-cognitive/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/GMaN1911/claude-cognitive/releases/tag/v1.0.0
