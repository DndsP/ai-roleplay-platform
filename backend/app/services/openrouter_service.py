from __future__ import annotations

import json
from typing import Any

import httpx

from backend.app.core.config import Settings
from backend.app.models.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    EvaluateRequest,
    EvaluationResponse,
    EvaluationScores,
    SessionDataResponse,
    SessionEvaluationResponse,
)


def _extract_json(content: str) -> dict[str, Any]:
    content = content.strip()
    if content.startswith("```"):
        parts = content.split("```")
        for part in parts:
            snippet = part.strip()
            if snippet.startswith("json"):
                snippet = snippet[4:].strip()
            if snippet.startswith("{") and snippet.endswith("}"):
                return json.loads(snippet)
    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end > start:
        return json.loads(content[start : end + 1])
    raise ValueError("Model response did not contain valid JSON.")


class OpenRouterService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def _headers(self) -> dict[str, str]:
        if not self.settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")
        return {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.settings.openrouter_referer,
            "X-Title": self.settings.openrouter_title,
        }

    async def _complete(self, model: str, messages: list[dict[str, str]]) -> str:
        async with httpx.AsyncClient(timeout=90.0, trust_env=False) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self._headers,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            payload = response.json()

        return payload["choices"][0]["message"]["content"].strip()

    async def generate_roleplay_reply(self, request: ChatRequest) -> ChatResponse:
        system_prompt = (
            f"You are {request.persona_name}, a roleplay persona in a training simulation. "
            f"Scenario: {request.scenario}. Goal: {request.persona_goal}. "
            "Stay in character, respond naturally, and keep replies between 2 and 5 sentences. "
            "Do not break character or describe yourself as an AI."
        )

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        messages.extend(
            {"role": msg.role, "content": msg.content} for msg in request.conversation_history
        )
        messages.append({"role": "user", "content": request.transcript})

        reply = await self._complete(self.settings.openrouter_model, messages)
        return ChatResponse(
            response=reply,
            persona_name=request.persona_name,
            scenario=request.scenario,
        )

    async def evaluate_response(self, request: EvaluateRequest) -> EvaluationResponse:
        system_prompt = (
            "You are a communication coach. Score the user's message from 1 to 10 for "
            "clarity, relevance, and confidence, then produce an overall score. "
            "Return strict JSON only with keys: scores, strengths, improvements, summary. "
            "scores must include clarity, relevance, confidence, overall."
        )
        user_prompt = (
            f"Scenario: {request.scenario}\n"
            f"Coaching goal: {request.coaching_goal}\n"
            f"User response: {request.transcript}"
        )
        content = await self._complete(
            self.settings.openrouter_evaluator_model,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        parsed = _extract_json(content)
        scores = EvaluationScores(**parsed["scores"])
        return EvaluationResponse(
            scores=scores,
            strengths=list(parsed.get("strengths", [])),
            improvements=list(parsed.get("improvements", [])),
            summary=parsed.get("summary", ""),
        )

    async def evaluate_session(self, session: SessionDataResponse) -> SessionEvaluationResponse:
        transcript = "\n".join(
            f"{segment.speaker_label}: {segment.text}" for segment in session.transcript_segments
        )
        system_prompt = (
            "You are an expert roleplay coach. Evaluate the entire session, not a single reply. "
            "Score the user from 1 to 10 for clarity, relevance, confidence, and overall performance. "
            "Use the full transcript and roleplay context. Return strict JSON only with keys: "
            "scores, strengths, improvements, summary. scores must include clarity, relevance, confidence, overall."
        )
        user_prompt = (
            f"Scenario: {session.context.scenario}\n"
            f"Persona: {session.context.persona_name}\n"
            f"Environment: {session.context.environment}\n"
            f"Persona goal: {session.context.persona_goal}\n"
            f"Participant name: {session.context.participant_name}\n"
            f"Full session transcript:\n{transcript}"
        )
        content = await self._complete(
            self.settings.openrouter_evaluator_model,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        parsed = _extract_json(content)
        scores = EvaluationScores(**parsed["scores"])
        return SessionEvaluationResponse(
            scores=scores,
            strengths=list(parsed.get("strengths", [])),
            improvements=list(parsed.get("improvements", [])),
            summary=parsed.get("summary", ""),
        )
