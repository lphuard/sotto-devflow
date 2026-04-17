# sotto-devflow

Standalone dev workflow orchestration for Sotto.

## Isolation Policy

This repository is **intentionally isolated** from `sotto-platform`. The following rules apply unconditionally:

- **No direct modification of sotto-platform** from this repo or its tooling.
- **No shared runtime, state, or config with sotto-platform.**
- **No access to or modification of `/home/sotto/.openclaw/workspace/sotto`** (the OpenClaw workspace root).
- **No PRs against sotto-platform** originating from this repo.

Any tooling, scripts, or automation in this repo must treat sotto-platform as a read-only external dependency at most, and must not write to, commit to, or push on behalf of sotto-platform.

## Purpose

`sotto-devflow` is a standalone orchestration layer for managing dev workflow tasks for the Sotto project. It handles task dispatch, state tracking, OpenHands integration, and reporting — independently of the sotto-platform runtime.

## Structure

```
src/
  cli/              # CLI entry points
  orchestrator/     # Task orchestration engine
  state/            # State store
  integrations/     # External integrations (OpenHands, etc.)
  schemas/          # JSON schemas for tasks and reports
runtime/
  tasks/            # Task queue (tracked)
  logs/             # Runtime logs (gitignored)
  reports/          # Generated reports (gitignored)
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # once dependencies are defined
```
