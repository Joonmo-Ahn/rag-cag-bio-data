# TODO (`rag-cag`)

> **Public 레포 주의**: 사내 데이터·경로·비밀키 등 민감 정보는 절대 적지 않고, 기술 구현과 학습 마일스톤만 기록합니다.

## 📍 Current Focus (다음 이어할 위치)

- **마지막 작업**: [notebooks/01_llm_client.ipynb](./notebooks/01_llm_client.ipynb) `Step 0` ~ `Step 4` 실습 완료
- **바로 이어할 작업**: `Step 5 (chat_vision)` → `Step 6 (src.core.llm 검증)` → `Step 7 (OpenRouter 모델 비교)`
- **스터디 노트**: [docs/study/01_llm_client_study.md](./docs/study/01_llm_client_study.md)

---

## 🔥 Now (지금 진행 중 — `01. Core LLM Client`)

- [x] `src/core/llm.py` 기본 구조 및 테스트([tests/test_llm_smoke.py](./tests/test_llm_smoke.py)) 확인
- [x] `01_llm_client.ipynb` `Step 0`: 환경 확인, `python-dotenv` `.env` 로드, 상수/타입 변수 `T`
- [x] `01_llm_client.ipynb` `Step 1`: `get_client()`
- [x] `01_llm_client.ipynb` `Step 2`: `_build_messages()`
- [x] `01_llm_client.ipynb` `Step 3`: `chat()`
- [x] `01_llm_client.ipynb` `Step 4`: `chat_structured()` (Pydantic + `.parse()`)
- [ ] `01_llm_client.ipynb` `Step 5`: `chat_vision()` 로컬 이미지 Base64 멀티모달 테스트
- [ ] `01_llm_client.ipynb` `Step 6`: `src.core.llm` 실제 모듈 대조 검증
- [ ] `01_llm_client.ipynb` `Step 7`: OpenRouter `/api/v1/models` 조회 및 후보 모델 벤치마크
- [ ] `uv run pytest -m "not live"` 및 `uv run pytest -m live -v` 실행 확인
- [ ] `Step 5~7` 내용 [docs/study/01_llm_client_study.md](./docs/study/01_llm_client_study.md)에 업데이트

---

## ⏭️ Next (다음 단계 모듈 — `src/` 폴더 기반)

- [ ] `src/ocr/`: `chat_vision()` 기반 문서/이미지 OCR 파이프라인 구현 및 노트북/스터디 정리
- [ ] `src/ontology/`: `chat_structured()` 기반 도메인 온톨로지·트리플 스키마 설계 및 추출기 구현
- [ ] `src/rag/`: 청킹·임베딩·검색 기반 RAG 파이프라인 구현
- [ ] `src/cag/`: 컨텍스트 캐싱 기반 CAG 파이프라인 구현

---

## 🧪 Later (평가 · 고도화)

- [ ] `eval/`: RAG vs CAG 품질·지연시간·비용 비교 평가 스크립트 및 지표 정리
- [ ] [SPEC.md](./SPEC.md)에 전체 아키텍처 및 데이터/평가 스펙 명세화
- [ ] `main.py` CLI/엔드투엔드 실행 엔트리포인트 연결
