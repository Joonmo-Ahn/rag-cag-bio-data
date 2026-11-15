# 01. OpenRouter LLM Client 스터디 노트

- **대응 노트북**: [01_llm_client.ipynb](../../notebooks/01_llm_client.ipynb)
- **대응 모듈**: [llm.py](../../src/core/llm.py)
- **진행 현황**: `Step 0` ~ `Step 4` 완료 / `Step 5` ~ `Step 7` 진행 예정
- **작성일**: 2026-11-16

---

## 1. 한 줄 요약 (TL;DR)

- `get_client()` → OpenRouter라는 **"통합 AI 창구"**로 연결되는 전용 전화기를 만드는 함수
- `chat()` → AI에게 자유롭게 **문자 답변**을 받는 기본 호출
- `chat_structured()` → AI에게 **빈칸이 정해진 설문지(`BaseModel`)**를 건네주고, 빈칸이 채워진 **파이썬 객체**로 바로 돌려받는 호출

---

## 2. 핵심 개념 쉽게 이해하기

### 2.1 `api_key: str | None = None` (`None = None`처럼 보이는 이유)

구조를 쪼개 보면 앞의 `None`과 뒤의 `None`은 역할이 완전히 다릅니다.

```text
api_key      : str | None        = None
[변수 이름]  : [허용되는 타입]   = [안 넘겼을 때의 기본값]
```

1. `def get_client(api_key):` → 반드시 값을 넘겨야 함
2. `def get_client(api_key=None):` → 생략하면 기본값 `None` 사용
3. `: str | None` → 타입 힌트 ("`str` 또는(`|`) `None`이 들어올 수 있음")
4. 합치면 **"문자열이나 `None`을 받을 수 있고, 생략하면 기본값 `None`을 쓴다"**는 뜻 (실제 동작은 `api_key=None`과 동일).

---

### 2.2 `default_headers={"X-Title": "rag-cag"}`

- **HTTP 헤더**: 택배로 치면 질문(`prompt`)은 상자 안의 물건(Body)이고, 헤더는 겉면의 **송장 정보**입니다.
- **`default_headers`**: 매 요청마다 적지 않고, `OpenAI(...)` 클라이언트를 만들 때 기본 송장 정보를 고정해 두는 옵션입니다.
- **`"X-Title"`**: OpenRouter 대시보드(Activity 로그)에서 **여러 프로젝트가 하나의 API 키를 공용으로 쓰더라도** 어느 프로젝트에서 나간 요청인지 이름으로 구분하기 위한 헤더입니다.
  - 참고: `X-`는 알파벳 순서가 아니라 HTTP 확장 헤더 관례 접두사이며, `Y-Title` 같은 것은 없습니다. (OpenRouter 지원 앱 헤더는 `X-Title`, `HTTP-Referer` 두 가지)

---

### 2.3 Structured Outputs: `ConceptSummary`, `Field`, `type[T]`, `.parse()`

```python
class ConceptSummary(BaseModel):
    term: str = Field(description="핵심 용어")
    definition: str = Field(description="한 줄 정의")
    use_cases: list[str] = Field(description="대표 활용 사례 2~3개")
```

- **`ConceptSummary(BaseModel)`**: AI에게 건네줄 **빈칸 채우기 설문지 양식(붕어빵 틀)**입니다. `BaseModel`은 일반 클래스에 "자동 유효성 검사 + JSON 변환" 능력을 붙여줍니다.
- **`Field(description="...")`**: 각 칸 옆에 붙이는 **작성 요령 스티커**입니다. `.parse()` 호출 시 이 설명 문구까지 AI에게 전달되어 AI가 칸의 의도에 맞게 채우도록 돕습니다.
- **`response_model: type[T]` -> `-> T`**:
  - `type[T]`는 `ConceptSummary()`(완성품)가 아니라 **`ConceptSummary`(붕어빵 틀 자체)**를 인자로 받는다는 뜻입니다.
  - `-> T`는 **"네가 넘긴 그 틀(`ConceptSummary`)로 찍어낸 완성품(`res.term`, `res.use_cases`를 바로 꺼낼 수 있는 객체)"**을 반환한다는 약속입니다.
  - 상단의 `T = TypeVar("T", bound=BaseModel)`은 `T` 자리에 반드시 `BaseModel`을 상속한 클래스만 올 수 있도록 제한합니다.
- **`.parse(...)`**:
  1. 파이썬 `BaseModel`을 AI가 이해하는 **JSON Schema**로 자동 번역해 전송
  2. AI가 스키마에 딱 맞는 JSON만 생성하도록 강제
  3. 응답을 자동 검증·역직렬화해서 **`message.parsed`(파이썬 객체)**로 반환

---

## 3. 왜 실무에서 이 방식을 쓰나? (대안 비교)

### 3.1 `.parse()` (Structured Outputs) vs 일반 `completions.create()` 수동 JSON 파싱

| 비교 항목 | 수동 방식 (`create()` + 프롬프트로 JSON 요청) | Structured Outputs (`.parse()` + `BaseModel`) |
| :--- | :--- | :--- |
| 출력 안정성 | AI가 사족(`네, 정리했습니다:`)이나 ` ```json ` 백틱, 키 오타를 내면 파싱 실패 가능 | API/모델 레벨에서 스키마에 맞는 출력만 허용하므로 파싱 실패가 거의 없음 |
| 후속 코드 | `json.loads()` 후 딕셔너리 키 오타 위험 | `res.term`처럼 IDE 자동완성 + Pydantic 타입 검증 자동 적용 |
| 실무 적합성 | 구형/소형 모델 호환용 폴백 | **RAG/CAG·온톨로지·지식그래프 추출의 현재 표준(Best Practice)** |

> **주의점**: OpenRouter의 아주 오래됐거나 작은 일부 모델은 `json_schema` 기반 Structured Outputs를 지원하지 않을 수 있으므로, `google/gemini-2.5-flash`, `openai/gpt-4o-mini` 등 지원 모델을 사용하는 것이 안전합니다.

### 3.2 OpenRouter API는 실제 서비스에서도 쓰나요?

- **많이 사용합니다.** 단일 API로 Gemini/Claude/GPT/Llama를 모델명만 바꿔 전환할 수 있고, 장애 시 자동 폴백과 통합 사용량 관리가 가능하기 때문입니다.
- 다만 1ms 단위의 초저지연이 필요하거나 엔터프라이즈 보안 계약(자체 VPC/직접 계약 등)이 필수인 서비스에서는 공식 API(OpenAI, Anthropic, Vertex AI 등)를 직접 연결하기도 합니다.

---

## 4. 내가 직접 막혔던 에러 노트 (Troubleshooting)

### 4.1 터미널에서 `export OPENROUTER_API_KEY=...` 했는데 노트북에서 `False`가 나온 문제

- **원인**: 터미널의 `export`는 해당 터미널 세션 안에서만 유효합니다. IDE의 Jupyter 커널은 별도 프로세스로 실행되므로 터미널의 `export` 값을 물려받지 못합니다.
- **해결**:
  1. 프로젝트 루트에 `.env` 파일 생성 (`OPENROUTER_API_KEY=...`, `.gitignore`에 `.env` 포함 확인)
  2. `uv add python-dotenv` 설치 후 노트북 `Step 0`에서 `from dotenv import load_dotenv; load_dotenv()` 호출

### 4.2 `AttributeError: 'tuple' object has no attribute 'chat'`

- **원인**: 대입문 맨 끝에 실수로 쉼표(`,`)를 붙였습니다.
  ```python
  active_client = client or get_client(),  # ❌ 끝의 쉼표 때문에 1개짜리 tuple이 됨!
  ```
- **해결**: 줄 끝의 쉼표(`,`) 제거 → `active_client = client or get_client()`

---

## 5. 다음 이어서 진행할 내용 (`Step 5 ~ Step 7`)

- [ ] `Step 5`: `chat_vision()` — 로컬 이미지 Base64 Data URI 인코딩 및 멀티모달 질의
- [ ] `Step 6`: `src.core.llm` 실제 모듈 임포트 & 노트북 구현과 대조 검증
- [ ] `Step 7`: OpenRouter `/api/v1/models` 모델 목록 조회 및 멀티 모델 비교 루프
