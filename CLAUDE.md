# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This repository is at a bare starting point: the only source file is `tasks-api/main.py` (note the nested `tasks-api/` directory inside the repo root). There is no dependency manifest, framework, test suite, linter config, or README yet. The project name suggests a tasks API, but no API code exists so far.

## Running

```
python tasks-api/main.py
```

`main.py` currently contains `Print ("hello world")`. That fails with a `NameError` because Python's built-in is lowercase `print`.

## Keeping this file current

When a framework, dependency file (e.g. `requirements.txt` / `pyproject.toml`), tests, or lint tooling is added, update this file with the real build/test/lint commands (including how to run a single test) and a short architecture overview.
