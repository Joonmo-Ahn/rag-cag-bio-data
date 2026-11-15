---
name: jupyter-lab-reference
description: >-
  Transforms a Python module (.py) into a hands-on Jupyter Notebook (.ipynb)
  learning reference. Use when the user wants to study, type out, and verify
  every component of a module step-by-step in Jupyter with detailed
  line-by-line technical explanations, purpose/rationale, and empty code cells
  for manual practice.
---

# Jupyter Lab Reference Generator

Convert a target Python module (or technical implementation) into a structured, self-contained `.ipynb` notebook designed for **hands-on typing** and **long-term technical reference**.

## Core Principles

1. **100% Module Completeness**:
   - Cover **every** import, module-level constant, `TypeVar`/type alias, internal helper (`_...`), and public function/class in the target `.py` file. Do not summarize or skip "boilerplate" lines.
2. **Markdown-First, Empty Code Cells**:
   - Place the reference code **inside the Markdown cell** above each execution slot, and leave the **Code cell below it completely empty** (`"source": []`) so the user can read, understand, and type the code themselves.
   - Never pre-fill the Code cells unless the user explicitly asks for pre-filled runnable cells.
3. **No Compressed Terminology**:
   - Explain technical concepts using exact terms (e.g., PEP 563 delayed annotations, `TypeVar` upper bounds, RFC 2397 Data URI, `sys.path` resolution order, fail-fast validation, dependency injection) rather than oversimplified metaphors.
4. **Security Hygiene**:
   - Never print full API keys or secrets. Always mask secrets (e.g., print `bool(key)` and a short prefix only).

---

## Required Notebook Structure

### 1. Title & Prerequisites Cell (Markdown)
- Notebook title referencing the target module path (e.g., `# 01. OpenRouter LLM Client Complete Lab (src/core/llm.py)`).
- Brief summary of what the notebook covers.
- Short prerequisite checklist (e.g., `ipykernel` installation, `.venv` kernel selection, environment variable check).

### 2. `Step 0`: Environment, `sys.path`, and Imports (Markdown + Empty Code Cell)
- Resolve `project_root` safely regardless of whether the Jupyter kernel starts in `notebooks/` or the repository root, and prepend it to `sys.path` so absolute imports (`from src...`) work.
- Verify required environment variables safely (masked output).
- Include all module-level imports, constants, and generic `TypeVar` / type definitions from the target `.py` file.

### 3. `Step 1 .. N`: Incremental Unit Breakdown (Markdown + Empty Code Cell per Step)
- Dedicate one Step to each cohesive unit (e.g., client factory, internal message builder, each public function or class).
- Include a minimal inline invocation or `print(...)` check at the end of each Step's reference code so the user can immediately verify that unit in isolation.

### 4. Final `Step`: Production Module Parity Verification (Markdown + Empty Code Cell)
- Import the actual target module (using aliases such as `as pkg_...` if names collide with functions defined earlier in the notebook).
- Verify constants, callability, and end-to-end behavior against the production module.

---

## Mandatory 3-Part Markdown Template per Step

Every Step's Markdown cell **must** follow this exact structure:

```markdown
## Step <N>. <Unit Name> — <Concise Role>

### 목적 및 의의
* **<Design Goal 1>**: <Why this unit exists in the broader system architecture.>
* **<Design Goal 2>**: <What problem or failure mode it prevents.>

### 레퍼런스 코드
```python
# Clean, runnable reference code for this step
```

### 라인별 상세 해설
* `<line or construct>`: <Exact technical reason it is used, runtime behavior, and design rationale.>
* `<line or construct>`: <...>
```

*(Adapt prose language to match the user's language, keeping technical identifiers and symbols in backticks.)*

---

## Output Format Checklist

- Output valid `nbformat` `4.5` JSON (`.ipynb`) with `"execution_count": null`, `"outputs": []`, and `"source": []` on all empty Code cells.
- Use list-of-strings or properly escaped `\n` strings in `"source"` so the JSON parses cleanly in JupyterLab, VS Code, and IDE notebook viewers.
- Validate that no trailing commas or unescaped quotes exist in the generated `.ipynb` JSON.
