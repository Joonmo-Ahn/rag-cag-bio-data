"""
[모듈 목적]
OpenRouter API를 통해 다양한 최신 LLM(텍스트, Structured Outputs, Vision 멀티모달)을
일관된 인터페이스로 호출하기 위한 공통 클라이언트 래퍼 모듈.

[설계 의의]
OCR, Ontology 추출, RAG, CAG 각 모듈이 개별적으로 HTTP/SDK 초기화 및 메시지 직렬화를
중복 구현하지 않도록 통신 계층을 `src/core/llm.py`로 단일화한다.
"""

# PEP 563 지연 평가 타입 어노테이션 활성화 (`str | None` 등 최신 유니온 문법 및 전방 참조를 런타임 오버헤드 없이 사용).
from __future__ import annotations

# 로컬 이미지 바이너리를 Data URI 스펙(`data:<mime>;base64,<payload>`)으로 인코딩하기 위한 표준 라이브러리.
import base64

# 파일 확장자 기반으로 MIME 타입(예: `image/png`, `image/jpeg`)을 추론하기 위한 표준 라이브러리.
import mimetypes

# 셸 환경변수(`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`)를 런타임에 조회하기 위한 표준 라이브러리.
import os

# OS 독립적인 파일 시스템 경로 조작 및 존재 여부 검증을 위한 객체 지향 경로 모듈.
from pathlib import Path

# `chat_structured`에서 호출자가 전달한 Pydantic 모델 타입 `T`를 반환 타입으로 그대로 보존하기 위한 제네릭 타입 변수.
from typing import TypeVar

# OpenRouter는 OpenAI Chat Completions API 스펙과 호환되므로 공식 `openai` SDK의 `base_url`만 치환하여 사용한다.
from openai import OpenAI

# LLM 출력을 지정된 JSON Schema로 강제·검증(Structured Outputs)하기 위한 데이터 검증 기반 클래스.
from pydantic import BaseModel

# OpenRouter의 OpenAI 호환 API 엔드포인트 루트 URL.
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# 명시적 `model` 인자가 없을 때 사용할 기본 모델 ID. 환경변수 `OPENROUTER_MODEL`로 런타임 오버라이드 가능.
DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")

# `BaseModel`을 상속한 임의의 스키마 클래스를 바인딩하기 위한 TypeVar.
T = TypeVar("T", bound=BaseModel)


def get_client(api_key: str | None = None) -> OpenAI:
    """
    OpenRouter 엔드포인트로 바인딩된 `OpenAI` 동기 클라이언트를 생성한다.

    인자로 `api_key`를 직접 전달하면 우선 사용하고, 생략 시 환경변수 `OPENROUTER_API_KEY`를 조회한다.
    """
    # 명시적 인자 > 환경변수 순으로 API 키를 해석한다.
    resolved_key = api_key or os.environ.get("OPENROUTER_API_KEY")

    # 키가 누락된 상태에서 네트워크 요청을 시도하지 않고, 원인 파악이 쉬운 예외를 즉시 발생시킨다.
    if not resolved_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Export it in your shell or .env file."
        )

    # OpenAI 기본 엔드포인트 대신 `OPENROUTER_BASE_URL`을 지정하여 OpenRouter 라우팅을 활성화한다.
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=resolved_key,
        # OpenRouter 대시보드 및 랭킹/사용량 로그에서 요청 출처 애플리케이션을 식별하기 위한 선택적 헤더.
        default_headers={
            "X-Title": "rag-cag",
        },
    )


def _build_messages(prompt: str, system: str | None = None) -> list[dict]:
    """
    OpenAI Chat Completions 규격에 맞는 `messages` 페이로드 리스트를 조립하는 내부 헬퍼.
    """
    messages: list[dict] = []

    # 시스템 프롬프트(페르소나, 출력 제약, 도메인 지시사항)가 주어졌을 때만 첫 번째 메시지로 삽입한다.
    if system:
        messages.append({"role": "system", "content": system})

    # 실제 태스크 입력에 해당하는 사용자 프롬프트를 추가한다.
    messages.append({"role": "user", "content": prompt})
    return messages


def chat(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    temperature: float = 0.2,
    max_tokens: int | None = None,
    client: OpenAI | None = None,
) -> str:
    """
    단일 텍스트 프롬프트에 대한 표준 Chat Completion 요청을 수행하고 응답 텍스트를 반환한다.

    - `temperature`: 샘플링 무작위성 제어 (결정론적 추출/테스트는 0.0 권장).
    - `max_tokens`: 생성 토큰 상한선.
    - `client`: 커넥션 풀 재사용이나 테스트 목(mock) 주입이 필요할 때 외부 `OpenAI` 인스턴스를 전달한다.
    """
    # 외부 주입 클라이언트가 없으면 기본 OpenRouter 클라이언트를 생성한다.
    active_client = client or get_client()

    # OpenRouter `/chat/completions` 엔드포인트 호출.
    response = active_client.chat.completions.create(
        model=model,
        messages=_build_messages(prompt, system),
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # 첫 번째 choice의 메시지 본문을 추출하며, `None`(예: tool_calls 전용 응답 등)인 경우 빈 문자열로 폴백한다.
    return response.choices[0].message.content or ""


def chat_structured(
    prompt: str,
    response_model: type[T],
    *,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    temperature: float = 0.0,
    client: OpenAI | None = None,
) -> T:
    """
    Pydantic 모델 스키마(`response_model`)를 강제하여 구조화된 객체(`T`)를 반환한다.

    Ontology 트리플(Entity-Relation) 추출, 메타데이터 파싱 등 후속 파이프라인에서
    타입 안전성이 필요한 태스크에 사용한다.
    """
    active_client = client or get_client()

    # `completions.parse`는 `response_model`을 JSON Schema로 직렬화해 API에 전달하고,
    # 응답 JSON을 자동으로 Pydantic 인스턴스로 역직렬화·검증한다.
    response = active_client.chat.completions.parse(
        model=model,
        messages=_build_messages(prompt, system),
        response_format=response_model,
        temperature=temperature,
    )

    # SDK가 파싱 및 스키마 검증을 완료한 Pydantic 객체 참조를 가져온다.
    parsed = response.choices[0].message.parsed

    # 모델 거부(refusal)나 스키마 불일치로 `parsed`가 `None`이면 조용히 넘기지 않고 명시적 예외를 발생시킨다.
    if parsed is None:
        raise ValueError("Model did not return a parsed structured response.")
    return parsed


def chat_vision(
    prompt: str,
    image_path: str | Path,
    *,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    temperature: float = 0.0,
    client: OpenAI | None = None,
) -> str:
    """
    로컬 이미지 파일을 Base64 Data URI로 인코딩하여 멀티모달(Vision) 모델에 질의한다.

    OCR 전처리 및 문서 레이아웃/표 추출 실험의 기본 진입점으로 사용한다.
    """
    # 문자열 또는 Path 입력을 `Path` 인스턴스로 정규화한다.
    path = Path(image_path)

    # 파일 미존재 시 인코딩 단계 이전에 조기 실패(fail-fast) 처리한다.
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    # 파일 확장자 기반 MIME 타입 추론; 판별 불가 시 보수적으로 `image/png`를 기본값으로 사용한다.
    mime_type, _ = mimetypes.guess_type(path)
    resolved_mime = mime_type or "image/png"

    # 바이너리 이미지를 읽고 Base64 ASCII 문자열로 인코딩하여 JSON 페이로드에 직접 삽입 가능하게 만든다.
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")

    # 멀티모달 입력 규격에 맞게 텍스트 파트와 이미지 URL 파트를 배열(`content`)로 구성한다.
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    # 외부 호스팅 URL 없이 로컬 파일을 직접 전송하기 위해 RFC 2397 Data URI 형식을 사용한다.
                    "image_url": {"url": f"data:{resolved_mime};base64,{encoded}"},
                },
            ],
        }
    )

    active_client = client or get_client()
    response = active_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""
