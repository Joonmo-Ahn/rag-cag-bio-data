# AGENTS.md (`rag-cag`)

## Environment & Tooling
- Python `>=3.13` managed with `uv` (`uv sync`, `uv run ...`).
- Secrets are stored in `.env` (`OPENROUTER_API_KEY`) and must never be committed.
- Tests:
  - Offline unit tests: `uv run pytest -m "not live"`
  - Live OpenRouter tests: `uv run pytest -m live -v`

## Repository Layout & Documentation Roles
- `src/`: Production Python modules (e.g. `src/core/llm.py`).
- `notebooks/`: Hands-on step-by-step practice notebooks (see `.agents/skills/jupyter-lab-reference/SKILL.md`).
- `docs/study/`: Concept explanations, practical trade-offs, and troubleshooting notes mapped 1:1 to notebooks (`docs/study/README.md`).
- Keep notebooks focused on technical reference + hands-on execution, and record conceptual Q&A, design decisions, and bug notes in `docs/study/`.
