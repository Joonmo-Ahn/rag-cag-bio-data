# 세션 기록: `uv`/IDE 폰트 세팅 ~ 파이썬 인자 문법 & `print_usage` 토큰·비용 추적

- **기간**: 2026-11-23 ~ 2026-11-25
- **작업 환경**: macOS (Apple Silicon MacBook Pro), `uv 0.13.9` (Homebrew `/opt/homebrew/bin/uv`), `.venv` (`Python 3.13.18`), Antigravity IDE
- **관련 레포**: `Joonmo-Ahn/rag-cag-bio-data` (`main`)

---

## 전체 흐름 한눈에 보기

```text
[11-23] uv 업데이트 (brew upgrade uv) & miniconda3 중복 uv PATH 충돌 해결, /opt 의미 이해
   ↓
[11-24] Open User Settings (JSON)에서 주피터(코드/마크다운/출력)·일반 에디터·터미널·마크다운 미리보기 폰트/행간 세팅
   ↓
[11-25] Antigravity 에이전트 창 & 좌측 사이드바 크기(window.zoomLevel) 확인
   ↓
[11-25] 01_llm_client.ipynb 학습: *, / *args / **kwargs / / 문법 원리 → print_usage() 구현 (getattr, 토큰·비용 구조, 포함/합성 OOP) → get_client / ConceptSummary 점검 → GitHub 푸시 & 세션 아카이브
```

---

## Part 1. `uv` 업데이트 & PATH 충돌 해결 (2026-11-23)

### Q1. `uv` 업데이트 명령어
- 시스템에 `uv`가 Homebrew(`/opt/homebrew/bin/uv`)로 설치되어 있으므로 `uv self update` 대신 **`brew upgrade uv`**를 사용 (`0.8.3` → `0.13.9`).
- 프로젝트 의존성 패키지 업데이트는 별개로 `uv sync --upgrade` (또는 특정 패키지 `uv lock --upgrade-package <pkg> && uv sync`).

### Q2. `brew upgrade uv` 후에도 버전이 그대로 보인 원인
- 터미널에서 `which uv` 확인 결과 **`/Users/jmahn/miniconda3/bin/uv`**가 잡힘.
- Conda `(base)` 환경이 활성화되어 `/Users/jmahn/miniconda3/bin`이 `/opt/homebrew/bin`보다 `PATH` 우선순위가 높았고, `miniconda3` 내부에 별도의 구버전 `uv`가 중복 설치되어 있었음.
- **권장 해결**: `miniconda3` 내부 `uv` 제거(`pip uninstall uv` 또는 `conda remove uv`) 후 `rehash`로 셸 캐시를 갱신해 `/opt/homebrew/bin/uv` 하나로 통일.

### Q3. `/opt` 경로의 의미
- `/opt` = **optional** (OS 기본 바이너리와 분리된 서드파티 소프트웨어 설치 영역).
- Apple Silicon Mac에서는 Homebrew 기본 경로가 `/opt/homebrew`이며, 특정 Conda 환경에 묶이지 않는 **전역 공용 `uv`**를 유지할 수 있어 충돌이 적고 관리가 깔끔함.

---

## Part 2. IDE(`settings.json`) 폰트·줄간격·UI 크기 세팅 (2026-11-24 ~ 11-25)

### Q4. Jupyter 노트북 폰트 설정 (`Open User Settings (JSON)`)
- `Cmd + Shift + P` → `Preferences: Open User Settings (JSON)`에서 영역별 3가지로 제어:
  - **코드 셀만 별도 지정**: `notebook.editorOptionsCustomizations` (`editor.fontFamily`, `editor.fontSize`, `editor.lineHeight`)
  - **마크다운 셀**: `notebook.markup.fontFamily`, `notebook.markup.fontSize`
  - **출력(Output) 영역**: `notebook.output.fontFamily`, `notebook.output.fontSize`, `notebook.output.lineHeight`

### Q5. `.json`과 `.py` 스크립트 폰트 크기
- 기본적으로 둘 다 최상위 `editor.fontSize`를 공유.
- 파일 종류별로 다르게 주려면 `[python]`, `[json]`, `[jsonc]` 언어별 블록으로 오버라이드 가능 (`settings.json`은 주석 허용 JSON이므로 `jsonc`도 함께 지정).

### Q6. 내장 터미널 & 마크다운 미리보기 폰트/행간
- **터미널**: `terminal.integrated.fontFamily`, `terminal.integrated.fontSize`, `terminal.integrated.lineHeight` (픽셀이 아니라 **배수**, 보통 `1.1`~`1.3`).
- **주피터 마크다운 셀 줄간격**: `notebook.markup.lineHeight` 같은 네이티브 키는 미지원 → 자체 행간이 여유 있는 서체(`Pretendard` — `brew install --cask font-pretendard`, 기존 설치된 `FiraCode Nerd Font` 확인) 적용 및 `fontSize` 조절로 보완.
- **일반 `.md` 미리보기**: `markdown.preview.fontFamily`, `markdown.preview.fontSize`, `markdown.preview.lineHeight` (`1.6` 추천)로 주피터 마크다운과 톤 통일.

### Q7. Antigravity 에이전트 창 & 좌측 사이드바 글자 크기
- 두 영역 모두 단독 `fontSize` 키가 없고 전체 UI 배율인 **`window.zoomLevel`** (`Cmd + +` / `Cmd + -` / `Cmd + 0`, 또는 `settings.json`에 `"window.zoomLevel": 0.5`)을 따름.
- **권장 세팅 순서**: `window.zoomLevel`로 좌측 사이드바와 에이전트 창 크기를 먼저 맞춘 뒤, 에디터·주피터·터미널의 개별 `fontSize`를 1~2px 보정.

---

## Part 3. 파이썬 인자 문법 & `print_usage` 구현 (2026-11-25)

### Q8. `01_llm_client.ipynb`의 단독 `*,`와 인자 기호 4가지 (`/`, `*`, `*args`, `**kwargs`)
- 단독 `*,`는 뒤쪽 인자를 **키워드 전용(`이름=값`)**으로 강제해 인자 순서 착각(`chat("안녕", "시스템")`이 `model`로 잘못 들어가는 실수 등)을 원천 차단.
- 순서 규칙: `위치전용(/) → 일반 → *args(또는 *) → 키워드전용 → **kwargs`.
- **핵심 원리 (PEP 3102)**: `*args`가 앞의 위치 인자를 무제한으로 다 삼켜버리기 때문에, `*args` 뒤에 오는 인자(`c`)는 필연적으로 `c=5`처럼 키워드로만 값을 줄 수 있음. 여기서 `args` 이름만 빼서 추가 위치 인자를 0개로 막은 것이 바로 단독 `*`.

### Q9. 입출력·사고 토큰 및 비용 출력 (`print_usage`)
- `chat()`, `chat_structured()`, `chat_vision()`이 모두 같은 `response.usage`를 반환하므로 공통 헬퍼 함수 `print_usage(response)`로 분리하고 `show_usage: bool = False` 옵션을 두는 설계가 기존 반환 타입(`-> str`, `-> T`)을 깨지 않아 가장 깔끔함.
- **토큰 & 비용 포함 관계**:
  - `out_tokens` (`completion_tokens`) = 눈에 보이는 답변 토큰 + `reasoning_tokens` (내부 사고 토큰)
  - `total_tokens` = `in_tokens` (`prompt_tokens`) + `out_tokens` (`completion_tokens`) — 서버 기준값 우선 사용하되 `usage.total_tokens or (in_tokens + out_tokens)`로 폴백 가능
  - `usage.cost` (OpenRouter 확장 필드): 입력 + 출력(사고 토큰 포함) 전체에 대해 실제 차감된 최종 비용(USD).

### Q10. `getattr` vs `dict.get` & 중첩 객체 구조(상속 vs 포함)
- `getattr(obj, "attr", default)`는 딕셔너리의 `d.get("key", default)`의 객체 버전. 단, **`getattr`은 3번째 인자(기본값)를 생략하면 `AttributeError`가 발생**하므로 반드시 기본값을 넣어야 안전.
- `response.usage.completion_tokens_details.reasoning_tokens`처럼 연달아 꺼낼 수 있는 이유는 상속(`is-a`)이 아니라 **포함/합성(`has-a`)** 구조 때문. 네트워크로는 JSON 텍스트가 오지만, `openai` SDK(Pydantic)가 이를 중첩 클래스 객체로 자동 파싱해서 전달함 (`response.model_dump()`로 다시 딕셔너리 확인 가능).

### Q11. `get_client()` 사용처 & `ConceptSummary`의 역할
- `get_client()`는 Step 1 테스트뿐 아니라 `chat()`, `chat_structured()`, `chat_vision()` 내부의 `client or get_client()`에서 매번 자동 호출되며, 대량 루프 시 커넥션 풀 재사용(`client = get_client()`)에도 활용됨.
- `ConceptSummary`는 `client`나 `src/core/llm.py`에 들어가는 것이 아니라, 노트북 Step 4에서 `chat_structured(..., response_model=ConceptSummary)`의 출력 스키마 예시로 임시 정의한 Pydantic 모델.

### Q12. GitHub 푸시 & 멀티 기기(MacBook Pro ↔ Mac mini) 세션 동기화
- `notebooks/01_llm_client.ipynb` 커밋(`8b899d0`) 후 `git push origin main` 완료.
- Antigravity 대화 기록은 각 기기 로컬(`~/.gemini/antigravity/brain/`)에 저장되므로, 집(Mac mini)과 맥북(MacBook Pro) 간 학습 맥락을 이어가기 위해 본 세션도 `docs/sessions/`에 아카이브하고 GitHub에 반영.
