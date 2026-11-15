# 세션 기록: 환경 세팅 ~ `01_llm_client.ipynb` (Step 0~4) & 레포 체계화

- **기간**: 2026-11-14 ~ 2026-11-16
- **작업 환경**: macOS 26.3 (arm64 Mac mini), Python 3.14.3 (시스템) / `>=3.13` (`uv 0.10.4` 프로젝트 `.venv`), Antigravity IDE
- **관련 레포**: `Joonmo-Ahn/rag-cag-bio-data` (`main`)

---

## 전체 흐름 한눈에 보기

```text
[11-14] 맥미니 Python & 워크스페이스 점검
   ↓
[11-15] IDE 단축키(⌘+L / ⌘+I) 충돌 해결 & .venv 인식 문서화 (code/md/python_venv_ide_setup.md)
   ↓
[11-15] 01_llm_client.ipynb Step 0~3 실습 (.env 로드 문제, TypeVar T, str|None=None, 쉼표 튜플 버그) & GitHub 첫 푸시
   ↓
[11-16] Step 4 실습 (BaseModel, Field, type[T], .parse() vs 수동 JSON) → docs/study/, README/AGENTS/TODO.md 체계화 & 푸시
```

---

## Part 1. 환경 점검 & 워크스페이스 전환 (2026-11-14)

### Q1. 맥미니와 현재 폴더 파이썬 환경 체크
- **질문**: 현재 폴더와 맥미니에 파이썬을 하려고 하는데 체크 요청.
- **확인 결과**:
  - 맥미니에 Homebrew `Python 3.14.3`, `pip3`, `uv 0.10.4`가 이미 설치되어 있음 (`conda`, `pyenv`는 미설치).
  - 당시 에이전트 세션은 하위 학습 폴더(`/Users/jmahn/project/study/Antigravity`)에 연결되어 있었고, 상위 `/Users/jmahn/project`는 별도 폴더로 열려 있는 멀티 루트 상태였음.

### Q2. 워크스페이스를 `/project` 폴더로 바꾸는 방법
- **핵심 정리**: 익스플로러에서 다른 폴더를 제거하거나 `Open Folder...`로 열더라도, **이미 열려 있는 채팅 세션은 시작 시점의 워크스페이스를 유지**함 → 폴더 변경 후 **새 채팅을 열어야** 새 워크스페이스로 반영됨.

---

## Part 2. IDE 단축키 & 가상환경 인식 정리 (2026-11-15)

### Q3. `⌘ + L`(사이드바 챗) / `⌘ + I`(인라인 챗) 단축키 문제
- **상황**: 주피터 셀이나 `.py`에서 `⌘ + I`를 누르면 인라인 챗 대신 코드 자동완성 목록(`Trigger Suggest`)이 뜸. 또한 키바인딩 설정 중 `Inline Chat: Accept Changes`에 잘못 지정하는 혼동 발생.
- **원인 & 해결**:
  - `⌘ + I`가 `editor.action.triggerSuggest` 및 `Chat: Start Voice Chat`과 겹쳐 있었음.
  - 인라인 챗을 **여는** 명령은 **`Inline Chat: Open Inline Chat` (`inlineChat.start`)**이며, 이를 안 겹치는 키(예: `⇧ + ⌘ + I`)로 변경하고 `Accept Changes`는 원래대로 되돌려 해결.

### Q4. 가상환경(`.venv`) 인식 설정 문서화
- `code` 폴더 내부 문서를 조사해 기존 문서가 없음을 확인한 뒤, 공용 문서 폴더(`code/md/`)에 `python_venv_ide_setup.md`를 생성해 인터프리터/커널 선택 및 `.vscode/settings.json` 고정 방법을 정리.

---

## Part 3. `01_llm_client.ipynb` Step 0 ~ Step 3 & GitHub 첫 푸시 (2026-11-15)

### Q5. `Parse error: Expected an identifier` & `T = TypeVar("T", bound=BaseModel)`의 `T`
- **오류 의미**: 식별자(변수/모듈 이름)가 올 자리에 이름이 비어 있거나 문법이 끊겼을 때 발생.
- **`T`의 의미**: 제네릭 타입 변수. `chat_structured(..., response_model: type[T]) -> T`에서 호출 시 넘긴 Pydantic 모델 타입을 반환 타입으로 그대로 보존하며, `bound=BaseModel`로 `BaseModel` 서브클래스만 허용하도록 제한함.

### Q6. 터미널에서 `export OPENROUTER_API_KEY=...` 했는데 노트북에서 `API key loaded: False`
- **원인**: `export`는 해당 터미널 프로세스 안에서만 유지되며, IDE의 Jupyter 커널 프로세스로 자동 전달되지 않음.
- **해결**: `pyproject.toml`에 `python-dotenv`를 추가하고 `.env` 파일 + `load_dotenv()`로 해결 (`API key loaded: True` 확인).

### Q7. GitHub 첫 푸시 (`rag-cag-bio-data`, Public)
- `.gitignore`에 `.env`, `data/` 등이 제외되는 것을 확인한 뒤 `Joonmo-Ahn/rag-cag-bio-data` Public 레포 생성 및 `Initial commit` (`ed1272a`) 푸시.

### Q8. `api_key: str | None = None` (`None = None`처럼 보이는 이유)
- **단계별 정리**:
  1. `api_key` → 필수 인자
  2. `api_key=None` → 생략 시 기본값 `None`
  3. `: str | None` → 타입 힌트 (`str` 또는 `None` 허용)
  4. 합치면 `[변수명]: [허용 타입] = [기본값]` 구조.

### Q9. `Parse error: Expected ')', found ':'` & `default_headers` / `X-Title` / OpenRouter 실서비스
- `OpenAI(...)` 키워드 인자에 `=` 대신 `:`를 쓰거나 `{`가 빠졌을 때 발생하는 구문 오류 해결.
- `default_headers={"X-Title": "rag-cag"}`는 매 요청에 붙는 기본 송장 정보로, **여러 프로젝트가 하나의 API 키를 공용으로 쓸 때** OpenRouter Activity 로그에서 프로젝트별 호출을 구분해 주는 역할을 함 (`Y-Title`은 없으며, `X-`는 HTTP 확장 헤더 접두사).
- OpenRouter는 멀티 모델 전환, 자동 폴백, 통합 과금 장점으로 실제 서비스에서도 널리 사용됨 (극단적 저지연이나 엔터프라이즈 VPC/직접 계약이 필수인 경우에만 공식 API 직접 연결).

### Q10. Step 3 실행 중 `AttributeError: 'tuple' object has no attribute 'chat'`
- **원인**: `active_client = client or get_client(),` 줄 끝의 **쉼표(`,`)** 때문에 `OpenAI` 객체가 아닌 `(OpenAI객체,)` 1원소 튜플이 대입됨.
- **해결**: 줄 끝 쉼표 제거 후 정상 실행 확인.

---

## Part 4. Step 4 이해 & 문서·할 일 체계화 (2026-11-16)

### Q11. Step 4 `type[T]`, `Field`, `ConceptSummary`, `.parse()` 직관적 이해 & 실무 적합성
- **비유**:
  - `ConceptSummary(BaseModel)`: AI에게 줄 **빈칸 채우기 설문지(붕어빵 틀)**
  - `Field(description="...")`: 각 칸 옆에 붙여 AI도 읽게 하는 **작성 요령 스티커**
  - `type[T]` vs `T`: **붕어빵 틀(`ConceptSummary`) 자체**를 넘기면, 그 틀로 구운 **완성품(`ConceptSummary` 인스턴스)**을 돌려준다는 약속
  - `.parse()`: Pydantic 모델을 JSON Schema로 번역해 전송하고, 스키마에 맞는 JSON만 생성하게 강제한 뒤 파이썬 객체(`message.parsed`)로 자동 변환·검증
- **실무 평가**: `.parse()` 없이 일반 `create()` + 프롬프트로 JSON을 강제할 수도 있지만 파싱 깨짐/사족 문제가 잦음. **온톨로지·RAG/CAG 추출에서는 `Pydantic + .parse()`가 현재 실무 표준(Best Practice)**.

### Q12. 스터디 문서·진입 파일·TODO 체계 구축 & GitHub 푸시
- **폴더 역할 분리**:
  - `notebooks/`: 손코딩 실습 레퍼런스
  - `docs/study/`: 개념 직관 · 실무 비교 · 트러블슈팅 노트 (`01_llm_client_study.md`, `README.md`)
  - `docs/sessions/`: 실제 대화 흐름 & 의사결정 기록 (현재 폴더)
  - 루트 진입 파일 정비: [README.md](../../README.md)(회사 PC 셋업 가이드), [AGENTS.md](../../AGENTS.md)(에이전트 온보딩 규칙), [TODO.md](../../TODO.md)(Now/Next/Later 로드맵) 작성 및 푸시.
