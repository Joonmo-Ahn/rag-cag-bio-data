# Study Notes (`rag-cag`)

`notebooks/`의 실습 코드([01_llm_client.ipynb](../../notebooks/01_llm_client.ipynb) 등)를 직접 타이핑·실행하면서 얻은 **개념 직관, 실무 설계 판단, 트러블슈팅 기록**을 정리하는 공간입니다.

- **노트북(`notebooks/`)**: 기술 원리·레퍼런스 코드 중심의 손코딩 실습
- **스터디 노트(`docs/study/`)**: 7살도 이해할 수 있는 쉬운 비유 + 왜 이 방법을 쓰는지(Trade-off) + 내가 막혔던 에러 기록

---

## 목차

| 번호 | 스터디 문서 | 대응 노트북 / 모듈 | 상태 |
| :---: | :--- | :--- | :--- |
| 01 | [01_llm_client_study.md](./01_llm_client_study.md) | [01_llm_client.ipynb](../../notebooks/01_llm_client.ipynb) · [llm.py](../../src/core/llm.py) | 진행 중 (`Step 0~4` 완료, `Step 5~7` 예정) |

---

## 문서 작성 템플릿 (4단 구성)

1. **한 줄 요약 (TL;DR)**: 핵심 개념을 가장 쉬운 비유로 요약
2. **핵심 개념 쉽게 이해하기**: 헷갈렸던 문법·구조 풀어쓰기
3. **왜 실무에서 이 방식을 쓰나? (대안 비교)**: 장단점 및 베스트 프랙티스
4. **내가 직접 막혔던 에러 노트 (Troubleshooting)**: 원인·해결법·재발 방지 팁
