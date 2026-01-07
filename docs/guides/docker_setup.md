# Docker Setup Guide

> Running claude-cognitive with Claude Code inside Docker containers

This guide covers setting up claude-cognitive in Docker environments, including Anthropic's official devcontainer setup.

---

## Overview

claude-cognitive works in Docker containers with some configuration. The key challenges are:

1. **Scripts must exist inside the container** at `~/.claude/scripts/`
2. **Hooks config must be in the container's** `~/.claude/settings.json`
3. **State files need persistence** across container restarts
4. **Path resolution** differs between host and container

---

## Architecture

### Data Flow Diagram

```
┌─────────────────────── HOST MACHINE ───────────────────────┐
│                                                            │
│  ~/my-project/                                             │
│  ├── src/                    (your code)                   │
│  ├── .claude/                (project documentation)       │
│  │   ├── CLAUDE.md                                         │
│  │   ├── systems/*.md                                      │
│  │   ├── modules/*.md                                      │
│  │   └── integrations/*.md                                 │
│  └── .devcontainer/          (container config)            │
│      ├── devcontainer.json                                 │
│      ├── Dockerfile                                        │
│      └── init-firewall.sh                                  │
│                                                            │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           │ bind mount: ~/my-project → /workspace
                           │ volume: claude-state → ~/.claude
                           ▼
┌─────────────────────── CONTAINER ──────────────────────────┐
│                                                            │
│  /workspace/                     (your mounted project)    │
│  └── .claude/                    ← PROJECT-LOCAL state     │
│      ├── CLAUDE.md                                         │
│      ├── systems/*.md                                      │
│      ├── modules/*.md                                      │
│      ├── attn_state.json         (attention scores)        │
│      └── pool/                                             │
│          └── instance_state.jsonl (coordination)           │
│                                                            │
│  /home/node/.claude/             ← GLOBAL fallback         │
│  ├── scripts/                    (claude-cognitive)        │
│  │   ├── context-router-v2.py                              │
│  │   ├── pool-loader.py                                    │
│  │   ├── pool-extractor.py                                 │
│  │   ├── pool-auto-update.py                               │
│  │   ├── pool-query.py                                     │
│  │   └── history.py                                        │
│  ├── settings.json               (hooks config)            │
│  ├── attention_history.jsonl     (history log)             │
│  └── pool/                       (global pool fallback)    │
│                                                            │
│  HOOK EXECUTION FLOW:                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. User types message                                │  │
│  │ 2. UserPromptSubmit hook fires                       │  │
│  │ 3. context-router-v2.py executes                     │  │
│  │ 4. Scans /workspace/.claude/ for documentation       │  │
│  │ 5. Computes attention scores (HOT/WARM/COLD)         │  │
│  │ 6. Injects relevant files into Claude's context      │  │
│  │ 7. pool-auto-update.py checks for coordination       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Path Resolution Strategy

claude-cognitive scripts use **project-local first, global fallback**:

```python
# From context-router-v2.py
PROJECT_STATE = Path(".claude/attn_state.json")           # Relative to CWD
GLOBAL_STATE = Path.home() / ".claude" / "attn_state.json"  # Container's ~

def get_state_file() -> Path:
    if PROJECT_STATE.parent.exists():  # .claude/ exists in CWD
        return PROJECT_STATE
    return GLOBAL_STATE  # Fallback to ~/.claude/
```

**This means:**
- Run `claude` from `/workspace` → uses `/workspace/.claude/`
- If no `.claude/` in CWD → uses `/home/node/.claude/`

---

## Quick Start (5 minutes)

### Prerequisites

- Docker installed
- Anthropic's devcontainer files (from [claude-code repo](https://github.com/anthropics/claude-code/tree/main/.devcontainer))

### Step 1: Add claude-cognitive to Dockerfile

Add these lines after the Claude Code installation:

```dockerfile
# Install claude-cognitive
RUN git clone https://github.com/GMaN1911/claude-cognitive.git /tmp/claude-cognitive && \
    mkdir -p /home/node/.claude/scripts && \
    cp -r /tmp/claude-cognitive/scripts/* /home/node/.claude/scripts/ && \
    chmod +x /home/node/.claude/scripts/*.py && \
    cp /tmp/claude-cognitive/hooks-config.json /home/node/.claude/settings.json && \
    rm -rf /tmp/claude-cognitive && \
    chown -R node:node /home/node/.claude
```

### Step 2: Set Environment Variables

Add to `devcontainer.json`:

```json
{
  "containerEnv": {
    "CLAUDE_INSTANCE": "DOCKER-A"
  }
}
```

### Step 3: Initialize Project Documentation

On your **host machine** (before building container):

```bash
cd ~/my-project
mkdir -p .claude/{systems,modules,integrations,pool}

# Create basic CLAUDE.md
cat > .claude/CLAUDE.md << 'EOF'
# My Project

**Project:** [Description]
**Status:** Development

## Quick Reference
- Start: `[command]`
- Test: `[command]`

## Architecture
[Describe your system]
EOF
```

### Step 4: Build and Run

```bash
# Build container
docker build -t claude-cognitive-dev .devcontainer/

# Run with your project mounted
docker run -it \
  -v "$(pwd):/workspace" \
  -e CLAUDE_INSTANCE=DOCKER-A \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  claude-cognitive-dev
```

### Step 5: Verify

Inside container:

```bash
cd /workspace
claude

# First message should show attention state header:
# ╔══ ATTENTION STATE [Turn 1] ══╗
# ║ 🔥 Hot: 0 │ 🌡️ Warm: 0 │ ❄️ Cold: X ║
```

---

## Full Devcontainer Setup

### Directory Structure

```
my-project/
├── .devcontainer/
│   ├── devcontainer.json
│   ├── Dockerfile
│   ├── init-firewall.sh        (from Anthropic)
│   └── claude-cognitive-hooks.json
├── .claude/
│   ├── CLAUDE.md
│   ├── systems/
│   ├── modules/
│   └── integrations/
└── src/
    └── (your code)
```

### devcontainer.json

```json
{
  "name": "Claude Code + Cognitive",
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python"
      ]
    }
  },
  "mounts": [
    "source=${localWorkspaceFolder},target=/workspace,type=bind",
    "source=claude-cognitive-state,target=/home/node/.claude-state,type=volume",
    "source=claude-bash-history,target=/commandhistory,type=volume"
  ],
  "containerEnv": {
    "CLAUDE_INSTANCE": "DOCKER-A",
    "CONTEXT_DOCS_ROOT": "/workspace/.claude"
  },
  "capAdd": ["NET_ADMIN", "NET_RAW"],
  "postCreateCommand": "sudo /usr/local/bin/init-firewall.sh",
  "postStartCommand": "cd /workspace && echo 'Ready for claude-cognitive!'",
  "remoteUser": "node"
}
```

### Dockerfile

```dockerfile
FROM node:20-bookworm

# Arguments
ARG CLAUDE_CODE_VERSION=latest
ARG ZSH_IN_DOCKER_VERSION=1.2.1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    sudo \
    vim \
    jq \
    python3 \
    python3-pip \
    iptables \
    ipset \
    dnsutils \
    fzf \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Set up node user
RUN echo "node ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/node && \
    chmod 0440 /etc/sudoers.d/node

# Install Oh My Zsh
USER node
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
    -t robbyrussell \
    -p git \
    -p fzf \
    -a "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history"

# Install Claude Code
USER root
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

# === CLAUDE-COGNITIVE INSTALLATION ===
RUN git clone https://github.com/GMaN1911/claude-cognitive.git /tmp/claude-cognitive && \
    mkdir -p /home/node/.claude/scripts && \
    cp -r /tmp/claude-cognitive/scripts/* /home/node/.claude/scripts/ && \
    chmod +x /home/node/.claude/scripts/*.py && \
    cp /tmp/claude-cognitive/hooks-config.json /home/node/.claude/settings.json && \
    rm -rf /tmp/claude-cognitive && \
    chown -R node:node /home/node/.claude

# Copy firewall script
COPY .devcontainer/init-firewall.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/init-firewall.sh && \
    echo "node ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/node-firewall && \
    chmod 0440 /etc/sudoers.d/node-firewall

# Set working directory
WORKDIR /workspace

USER node
ENV SHELL=/bin/zsh
CMD ["/bin/zsh"]
```

---

## State Persistence

### Option 1: Named Volume (Recommended)

State persists across container rebuilds:

```json
{
  "mounts": [
    "source=claude-cognitive-state,target=/home/node/.claude,type=volume"
  ]
}
```

### Option 2: Bind Mount to Host

State visible on host filesystem:

```json
{
  "mounts": [
    "source=${localEnv:HOME}/.claude-docker,target=/home/node/.claude,type=bind"
  ]
}
```

### Option 3: Project-Local Only

All state in project `.claude/` directory (simplest):

```bash
# State files created in /workspace/.claude/
# Automatically included in git (add to .gitignore if needed)
```

Add to `.gitignore`:
```
.claude/attn_state.json
.claude/pool/instance_state.jsonl
```

---

## Multi-Container Coordination

### Running Multiple Containers

Each container needs a unique `CLAUDE_INSTANCE`:

```bash
# Terminal 1 - Container A
docker run -e CLAUDE_INSTANCE=DOCKER-A ...

# Terminal 2 - Container B
docker run -e CLAUDE_INSTANCE=DOCKER-B ...

# Terminal 3 - Container C
docker run -e CLAUDE_INSTANCE=DOCKER-C ...
```

### Shared Pool Coordination

For containers to coordinate, they must share the pool file:

**Option 1: Shared Volume**
```yaml
# docker-compose.yml
version: '3.8'
services:
  claude-a:
    image: claude-cognitive-dev
    environment:
      - CLAUDE_INSTANCE=DOCKER-A
    volumes:
      - ./project:/workspace
      - shared-pool:/home/node/.claude/pool

  claude-b:
    image: claude-cognitive-dev
    environment:
      - CLAUDE_INSTANCE=DOCKER-B
    volumes:
      - ./project:/workspace
      - shared-pool:/home/node/.claude/pool

volumes:
  shared-pool:
```

**Option 2: Host Bind Mount**
```bash
# Both containers mount same host directory
docker run -v ~/.claude-shared/pool:/home/node/.claude/pool ...
```

---

## Environment Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `CLAUDE_INSTANCE` | Pool coordination identifier | `?` | `DOCKER-A` |
| `CONTEXT_DOCS_ROOT` | Override docs location | `~/.claude` | `/workspace/.claude` |
| `POOL_COMPACT` | Compact pool output | `1` | `0` for verbose |

---

## Troubleshooting

### "No ATTENTION STATE header"

**Cause:** Hooks not configured or scripts not found

**Fix:**
```bash
# Check hooks config exists
cat ~/.claude/settings.json

# Check scripts exist
ls -la ~/.claude/scripts/

# Test router manually
echo '{"prompt":"test"}' | python3 ~/.claude/scripts/context-router-v2.py
```

### "Scripts not found" errors

**Cause:** Scripts not copied to container

**Fix:**
```bash
# Inside container
ls ~/.claude/scripts/

# If empty, manually install:
git clone https://github.com/GMaN1911/claude-cognitive.git /tmp/cc
cp -r /tmp/cc/scripts/* ~/.claude/scripts/
chmod +x ~/.claude/scripts/*.py
```

### "Permission denied" on scripts

**Cause:** Scripts not executable

**Fix:**
```bash
chmod +x ~/.claude/scripts/*.py
```

### State not persisting

**Cause:** No volume mount for `~/.claude/`

**Fix:** Add volume mount to devcontainer.json:
```json
{
  "mounts": [
    "source=claude-cognitive-state,target=/home/node/.claude,type=volume"
  ]
}
```

### Pool coordination not working between containers

**Cause:** Containers using separate pool files

**Fix:** Ensure shared volume or bind mount for pool directory.

---

## VS Code Remote Containers

### Opening in Container

1. Install "Remote - Containers" extension
2. Open project folder
3. Click "Reopen in Container" when prompted
4. Wait for build to complete

### Terminal Access

Use VS Code's integrated terminal - it runs inside the container.

### Rebuilding

After modifying Dockerfile:
1. Command Palette → "Remote-Containers: Rebuild Container"

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Claude Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/your-org/claude-cognitive-dev:latest

    steps:
      - uses: actions/checkout@v4

      - name: Initialize claude-cognitive
        run: |
          mkdir -p ~/.claude/scripts
          cp -r /opt/claude-cognitive/scripts/* ~/.claude/scripts/

      - name: Run Claude Code
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          CLAUDE_INSTANCE: CI-${{ github.run_id }}
        run: |
          cd $GITHUB_WORKSPACE
          claude --print "Review the changes in this PR"
```

---

## Security Considerations

### Firewall Integration

Anthropic's `init-firewall.sh` restricts network access. claude-cognitive scripts don't require external network access, so they work within the firewall rules.

### Sensitive Data

- API keys should be passed via environment variables, not stored in container
- Pool files may contain work summaries - consider `.gitignore` if sensitive
- Attention history logs conversation keywords

### Volume Permissions

```bash
# Ensure node user owns .claude directory
sudo chown -R node:node /home/node/.claude
```

---

## Quick Reference

### Common Commands

```bash
# Build container
docker build -t claude-dev .devcontainer/

# Run interactive
docker run -it -v "$(pwd):/workspace" -e CLAUDE_INSTANCE=A claude-dev

# Check claude-cognitive status
python3 ~/.claude/scripts/pool-query.py --since 1h

# View attention history
python3 ~/.claude/scripts/history.py --last 20

# Check logs
tail -f ~/.claude/context_injection.log
```

### File Locations (Inside Container)

| File | Purpose |
|------|---------|
| `~/.claude/scripts/` | claude-cognitive scripts |
| `~/.claude/settings.json` | Hooks configuration |
| `~/.claude/attention_history.jsonl` | Turn-by-turn history |
| `/workspace/.claude/` | Project documentation |
| `/workspace/.claude/attn_state.json` | Attention scores |
| `/workspace/.claude/pool/` | Pool coordination |

---

## Related Documentation

- [Getting Started](./getting-started.md) - Non-Docker setup
- [Pool Coordination](../concepts/pool-coordination.md) - Multi-instance patterns
- [Attention Decay](../concepts/attention-decay.md) - How files fade
- [Anthropic DevContainer Docs](https://docs.claude.com/en/docs/claude-code/devcontainer)

---

## Contributing

Found an issue with Docker setup? Please report it:
- [GitHub Issues](https://github.com/GMaN1911/claude-cognitive/issues)
- [GitHub Discussions](https://github.com/GMaN1911/claude-cognitive/discussions)

---

**Last Updated:** January 2026
**Tested With:** Claude Code v2.0.x, Docker 24.x, Node 20
