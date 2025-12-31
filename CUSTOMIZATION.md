# Customizing claude-cognitive for Your Project

The scripts work out-of-the-box, but **you should customize keywords** to match your codebase for maximum effectiveness.

---

## Quick Start (Skip Customization)

**The scripts will work immediately with minimal setup:**
- They'll detect file mentions from your actual messages
- Co-activation will happen based on file proximity in `.claude/` structure
- Token savings will still be 50-70% without customization

**But for 80-95% savings:** Customize keywords to match your domain.

---

## What Needs Customization

### `scripts/context-router-v2.py`

This file contains **keyword mappings** - what words activate which files.

**Example from MirrorBot (shipped version):**
```python
KEYWORDS: Dict[str, List[str]] = {
    "systems/legion.md": [
        "legion", "5090", "rtx 5090", "local model", "vram", "oom"
    ],
    "systems/orin.md": [
        "orin", "jetson", "sensory", "layer 0", "ppe"
    ],
}
```

**Your customization:**
```python
KEYWORDS: Dict[str, List[str]] = {
    "systems/production.md": [
        "prod", "production", "deployment", "kubernetes", "k8s"
    ],
    "systems/staging.md": [
        "staging", "test env", "qa", "integration tests"
    ],
    "modules/auth.md": [
        "authentication", "login", "oauth", "jwt", "session"
    ],
    "modules/database.md": [
        "database", "postgres", "sql", "migrations", "schema"
    ],
}
```

---

## Step-by-Step Customization

### 1. Map Your `.claude/` Structure

First, list what you have:

```bash
ls .claude/systems/
ls .claude/modules/
ls .claude/integrations/
```

**Example output:**
```
systems/production.md
systems/staging.md
modules/auth.md
modules/api.md
modules/database.md
integrations/stripe.md
```

### 2. Identify Keywords for Each File

For each file, ask: **"What words would make me want to see this file?"**

**Example: `modules/auth.md`**
- Direct mentions: "auth", "authentication", "login"
- Related concepts: "oauth", "jwt", "session", "token"
- Technical terms: "passport.js", "bcrypt", "password reset"
- Common questions: "how do users log in", "session management"

### 3. Edit `context-router-v2.py`

Open the file:
```bash
nano ~/.claude/scripts/context-router-v2.py
```

Find the `KEYWORDS` section (around line 75):

**Before (MirrorBot example):**
```python
KEYWORDS: Dict[str, List[str]] = {
    "systems/legion.md": [
        "legion", "5090", "rtx 5090", ...
    ],
    # ... many MirrorBot-specific entries
}
```

**After (your project):**
```python
KEYWORDS: Dict[str, List[str]] = {
    # === SYSTEMS ===
    "systems/production.md": [
        "prod", "production", "deploy", "kubernetes", "k8s", "live"
    ],
    "systems/staging.md": [
        "staging", "test", "qa", "integration", "pre-prod"
    ],

    # === MODULES ===
    "modules/auth.md": [
        "auth", "authentication", "login", "oauth", "jwt", "session",
        "passport", "bcrypt", "password", "reset", "signup", "signin"
    ],
    "modules/api.md": [
        "api", "endpoint", "route", "express", "fastapi", "rest",
        "graphql", "controller", "handler"
    ],
    "modules/database.md": [
        "database", "db", "postgres", "sql", "orm", "sequelize",
        "migration", "schema", "query", "models"
    ],

    # === INTEGRATIONS ===
    "integrations/stripe.md": [
        "stripe", "payment", "billing", "subscription", "checkout",
        "webhook", "invoice", "customer"
    ],
}
```

### 4. Update Co-Activation Graph (Optional)

The `CO_ACTIVATION` section (around line 185) defines which files boost each other.

**Example:**
```python
CO_ACTIVATION: Dict[str, List[str]] = {
    # When auth is mentioned, also boost API and database
    "modules/auth.md": [
        "modules/api.md",      # Auth uses API routes
        "modules/database.md", # Auth stores sessions in DB
    ],

    # When Stripe is mentioned, boost API and webhooks
    "integrations/stripe.md": [
        "modules/api.md",      # Stripe webhooks hit API
        "modules/webhooks.md", # Webhook processing
    ],
}
```

### 5. Adjust Decay Rates (Optional)

Different file categories fade at different rates:

```python
DECAY_RATES = {
    "systems/": 0.85,       # Infrastructure is stable
    "modules/": 0.70,       # Code changes frequently
    "integrations/": 0.80,  # APIs semi-stable
    "docs/": 0.75,          # Documentation medium
    "default": 0.70
}
```

**Higher number = slower decay** (file stays relevant longer)

---

## Testing Your Customization

### 1. Check Keyword Activation

Start Claude Code and say:
```
I need to debug the authentication flow
```

Then check if `modules/auth.md` activated:
```bash
tail -20 ~/.claude/context_injection.log
```

Should see:
```
[HOT] modules/auth.md (score: 1.00)
```

### 2. Verify Co-Activation

If you mention auth, related files should warm up:
```
Show me how authentication works
```

Check log:
```
[HOT] modules/auth.md (score: 1.00)
[WARM] modules/api.md (score: 0.35)
[WARM] modules/database.md (score: 0.35)
```

### 3. Test Decay

In subsequent messages without mentioning auth:
```
How does the frontend work?
```

Auth should decay:
```
[WARM] modules/auth.md (score: 0.70)  # 1.0 * 0.70 decay
```

---

## Common Patterns

### Web Application
```python
KEYWORDS = {
    "systems/frontend.md": [
        "frontend", "react", "vue", "ui", "component", "css"
    ],
    "systems/backend.md": [
        "backend", "api", "server", "node", "express", "django"
    ],
    "modules/auth.md": [
        "auth", "login", "jwt", "session"
    ],
    "modules/database.md": [
        "database", "postgres", "sql", "orm"
    ],
}
```

### Microservices
```python
KEYWORDS = {
    "systems/user-service.md": [
        "user service", "users", "accounts", "profiles"
    ],
    "systems/payment-service.md": [
        "payment", "billing", "stripe", "transactions"
    ],
    "integrations/kafka.md": [
        "kafka", "event bus", "messaging", "queue"
    ],
}
```

### Data Pipeline
```python
KEYWORDS = {
    "modules/ingestion.md": [
        "ingestion", "data collection", "sources", "extract"
    ],
    "modules/transformation.md": [
        "transform", "etl", "clean", "normalize"
    ],
    "modules/storage.md": [
        "storage", "s3", "data lake", "warehouse"
    ],
}
```

---

## Tips for Good Keywords

### ✅ DO:
- **Include common variations**: "auth", "authentication", "login"
- **Add technical terms**: "jwt", "oauth", "bcrypt"
- **Include error messages**: "401", "unauthorized", "invalid token"
- **Think like your questions**: "how do users log in"

### ❌ DON'T:
- Use overly generic words ("the", "system", "code")
- Duplicate keywords across unrelated files
- Add keywords just to have more (quality > quantity)

---

## Validation Script

Check your keyword mapping:

```bash
# From project root
python3 - <<EOF
import sys
sys.path.insert(0, str(Path.home() / ".claude/scripts"))
from context_router_v2 import KEYWORDS, CO_ACTIVATION

print("Files mapped:", len(KEYWORDS))
print("\nKeywords per file:")
for file, keywords in sorted(KEYWORDS.items()):
    print(f"  {file}: {len(keywords)} keywords")

print("\nCo-activations:")
for file, related in sorted(CO_ACTIVATION.items()):
    print(f"  {file} → {len(related)} related files")
EOF
```

---

## When to Recustomize

**Recustomize when:**
- ✅ Adding new files to `.claude/`
- ✅ Files aren't activating when you expect
- ✅ Frequently typing the same thing without file activation
- ✅ Token usage higher than expected

**Don't customize if:**
- ❌ It's working well
- ❌ You just set it up (give it time)
- ❌ Making it perfect (good enough is fine)

---

## Getting Help

**If keywords aren't working:**
1. Check logs: `tail -f ~/.claude/context_injection.log`
2. Verify file paths match `.claude/` structure
3. Try more specific keywords
4. Post in GitHub Discussions with example

**If co-activation isn't working:**
1. Check CO_ACTIVATION graph
2. Verify file names match exactly
3. Start with direct mentions first

---

## Remember

**The shipped MirrorBot keywords work as an example.**

You'll still get 50-70% token savings without customization. Customization gets you to 80-95%.

Start simple. Iterate based on actual usage. Perfection isn't required.
