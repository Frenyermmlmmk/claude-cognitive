# Task API - Simple Example

**Purpose:** Minimal example demonstrating claude-cognitive

This is a tiny REST API for task management, used to show how claude-cognitive works with a small project.

---

## What This Demonstrates

✅ **Context Router:**
- Files organized in `.claude/` directory
- Systems, modules, integrations structure
- Documentation at appropriate detail levels

✅ **Pool Coordinator:**
- Manual pool blocks for coordination
- Instance-based work sharing

✅ **Best Practices:**
- Minimal but complete documentation
- Fractal structure (high-level → detailed)
- Project-local configuration

---

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy
```

### 2. Start Server

```bash
python src/main.py
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000/health

# Create task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"Example"}'

# List tasks
curl http://localhost:8000/tasks
```

### 4. Use with Claude Code

```bash
# Set instance ID
export CLAUDE_INSTANCE=A

# Start Claude Code
cd /path/to/this/example
claude
```

**In Claude:**
```
How does the task creation endpoint work?
```

Watch for `ATTENTION STATE` header showing context injection!

---

## File Structure

```
small-project/
├── .claude/                    # Claude Cognitive config
│   ├── CLAUDE.md              # Project overview
│   ├── systems/
│   │   └── local-dev.md       # Local environment
│   └── modules/
│       ├── api.md             # API documentation
│       └── tasks.md           # Task manager docs
├── src/
│   ├── main.py                # FastAPI entry point
│   ├── tasks.py               # Task business logic
│   └── database.py            # SQLite setup
├── tests/
│   └── test_api.py            # API tests
└── README.md                  # This file
```

---

## Context Router in Action

**Scenario:** You ask about task creation

1. **Mention detected:** "task creation" → activates `modules/api.md`
2. **Co-activation:** `modules/tasks.md` also boosted (related)
3. **Injection:** Both files injected as context
4. **Result:** Claude has full context for your question

**Over time:**
- Files you use frequently stay HOT
- Related files stay WARM
- Unused files decay to COLD

---

## Pool Coordination Example

**If working with a team:**

```bash
# Developer A
export CLAUDE_INSTANCE=A
```

In Claude (Instance A):
```pool
INSTANCE: A
ACTION: completed
TOPIC: Added task filtering endpoint
SUMMARY: Implemented GET /tasks?status=completed filter. Updated tests.
AFFECTS: src/main.py, src/tasks.py, tests/test_api.py
BLOCKS: Can now work on pagination
```

**Developer B starts session:**
```bash
export CLAUDE_INSTANCE=B
claude
```

Instance B sees:
```
## Session Context
- **Instance**: B
- **Pool**: 1 recent

### Recent Activity
- [A] completed: Added task filtering endpoint
```

Instance B now knows filtering is done, can work on pagination!

---

## Learning Points

**This example shows:**

1. **Minimal viable docs** - Just enough for claude-cognitive to work
2. **Fractal structure** - High-level in CLAUDE.md, details in modules
3. **Project-local setup** - `.claude/` in project root
4. **Real workflow** - How context router and pool work together

**For your project:**
- Start simple (like this)
- Add detail as needed
- Keep docs updated

---

## Next Steps

**Try it yourself:**
1. Copy this example
2. Run the server
3. Start Claude Code with instance ID
4. Ask questions about the code
5. Watch context injection work

**Then:**
- See `monorepo` example for larger projects
- See `mirrorbot-sanitized` for production-scale example
- Read full documentation in main repo

---

**Part of:** [claude-cognitive](https://github.com/GMaN1911/claude-cognitive)

**License:** MIT
