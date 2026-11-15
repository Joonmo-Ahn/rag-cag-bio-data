"""
[모듈 목적]
`src/core/llm.py`의 설정 무결성(오프라인 단위 테스트)과 OpenRouter 실제 엔드포인트 연동(라이브 스모크 테스트)을
분리하여 검증하는 테스트 스위트.

[실행 방법]
- 오프라인 단위 테스트만 실행: `uv run pytest -m "not live"`
- 실제 OpenRouter API 호출 포함: `uv run pytest -m live -v`
"""

# 라이브 테스트 실행 전 API 키 존재 여부를 판별하기 위해 사용한다.
import os

# 테스트 픽스처(`monkeypatch`), 예외 검증(`pytest.raises`), 마커(`@pytest.mark.live`)를 제공한다.
import pytest

# Structured Outputs 라이브 스모크 테스트에서 스키마 계약을 정의하기 위한 기반 모델.
from pydantic import BaseModel

# 검증 대상인 OpenRouter 상수 및 클라이언트/호출 함수 임포트.
from src.core.llm import OPENROUTER_BASE_URL, chat, chat_structured, get_client


def test_get_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    환경변수 `OPENROUTER_API_KEY`가 없고 인자도 전달되지 않았을 때
    `get_client()`가 조용히 진행하지 않고 `RuntimeError`를 발생시키는지 검증한다.
    """
    # `monkeypatch`로 현재 테스트 함수 스코프 내에서만 `OPENROUTER_API_KEY`를 제거한다(종료 시 자동 복원).
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    # 에러 메시지에 `OPENROUTER_API_KEY` 문자열이 포함된 `RuntimeError`가 발생해야 테스트가 통과한다.
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        get_client()


def test_get_client_uses_openrouter_base_url() -> None:
    """
    생성된 `OpenAI` 클라이언트의 `base_url`이 OpenAI 기본 주소가 아닌
    `OPENROUTER_BASE_URL`로 정확히 설정되는지 네트워크 요청 없이 검증한다.
    """
    # 더미 API 키를 주입해 클라이언트 객체 초기화만 수행한다.
    client = get_client(api_key="sk-or-test-key")

    # `httpx.URL`로 정규화된 `base_url`의 후행 슬래시(`/`)를 제거해 상수와 정확히 일치하는지 단언(assert)한다.
    assert str(client.base_url).rstrip("/") == OPENROUTER_BASE_URL


@pytest.mark.live
def test_live_openrouter_chat_and_structured() -> None:
    """
    실제 OpenRouter API를 호출해 텍스트 응답(`chat`)과 구조화 출력(`chat_structured`)이
    엔드투엔드로 동작하는지 검증하는 라이브 스모크 테스트.
    """
    # CI나 오프라인 환경에서 실수로 실패 처리되지 않도록 API 키 미설정 시 테스트를 skip한다.
    if not os.environ.get("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY is not set")

    # 1. 기본 텍스트 Chat Completion 검증: 결정론적 응답(`temperature=0.0`)과 최소 토큰 제한 사용.
    reply = chat("Reply with exactly: OK", temperature=0.0, max_tokens=16)
    assert "OK" in reply.upper()

    # 2. Structured Outputs 검증: 응답이 Pydantic 모델 `PingResult` 스키마에 맞게 파싱되는지 확인.
    class PingResult(BaseModel):
        status: str

    parsed = chat_structured(
        "Return status='ok'.",
        PingResult,
    )
    assert parsed.status.lower() == "ok"
