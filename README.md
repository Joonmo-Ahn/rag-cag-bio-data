# rag-cag

OpenRouter API 기반으로 LLM(텍스트, Structured Outputs, Vision 멀티모달), OCR, Ontology, RAG/CAG 실험을 단계별로 구현하고 학습하는 프로젝트입니다.

---

## 프로젝트 구조

```text
rag-cag/
├── src/
│   └── core/
│       └── llm.py            # OpenRouter 공통 LLM 클라이언트 래퍼
├── notebooks/
│   └── 01_llm_client.ipynb   # Step별 손코딩 실습 노트북
├── docs/
│   └── study/                # 개념 직관 · 설계 비교 · 트러블슈팅 노트
│       ├── README.md
│       └── 01_llm_client_study.md
├── tests/
│   └── test_llm_smoke.py     # 단위 & OpenRouter 라이브 스모크 테스트
├── pyproject.toml
└── uv.lock
```

---

## 다른 PC(회사 등)에서 이어서 시작하기

`.env`와 `.venv`는 `.gitignore`에 의해 GitHub에 올라가지 않으므로, 새 PC에서는 아래 4단계로 환경을 맞춘 뒤 바로 이어서 진행하면 됩니다.

### 1. 코드 받아오기
```bash
git clone https://github.com/Joonmo-Ahn/rag-cag-bio-data.git
cd rag-cag-bio-data
# 이미 clone한 폴더가 있다면:
# git pull
```

### 2. 가상환경 및 패키지 동기화 (`uv`)
```bash
uv sync
```

### 3. `.env` 파일 생성
프로젝트 루트에 `.env` 파일을 만들고 OpenRouter API 키를 입력합니다.
```env
OPENROUTER_API_KEY=sk-or-v1-...
```

### 4. 테스트 & 노트북 실행
- 오프라인 단위 테스트:
  ```bash
  uv run pytest -m "not live"
  ```
- Jupyter 노트북([notebooks/01_llm_client.ipynb](./notebooks/01_llm_client.ipynb)):
  - IDE 우측 상단 **`Select Kernel`** → `.venv` (`Python 3.13`) 선택
  - 이어할 스터디 노트: [docs/study/01_llm_client_study.md](./docs/study/01_llm_client_study.md)

---

## 스터디 문서 & 할 일

- 전체 스터디 목차: [docs/study/README.md](./docs/study/README.md)
- 진행 현황 & 할 일: [TODO.md](./TODO.md)
