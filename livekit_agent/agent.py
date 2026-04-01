from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, silero, simli


logger = logging.getLogger("ai_roleplay_livekit_agent")
logger.setLevel(logging.INFO)

load_dotenv()


DEFAULT_INSTRUCTIONS = (
    "You are a roleplay training partner. Stay in character, respond naturally, "
    "and keep the conversation flowing like a live call."
)
DEFAULT_AGENT_NAME = "roleplay-agent"


def _build_instructions(
    base_instructions: str,
    scenario: str,
    persona_name: str,
    persona_goal: str,
    environment: str,
) -> str:
    return (
        f"{base_instructions}\n\n"
        "Session roleplay context:\n"
        f"- Scenario: {scenario}\n"
        f"- Persona name: {persona_name}\n"
        f"- Environment: {environment}\n"
        f"- Persona goal: {persona_goal}\n\n"
        f"You are {persona_name}. Stay fully in character for the entire conversation. "
        "Respond like a real person in this situation, not like an assistant. "
        "Ask follow-up questions naturally when appropriate, keep the conversation coherent across the full session, "
        "and use the prior turns as memory for the ongoing interaction."
    )


async def entrypoint(ctx: JobContext) -> None:
    base_instructions = os.getenv("LIVEKIT_AGENT_INSTRUCTIONS", DEFAULT_INSTRUCTIONS)
    simli_api_key = os.getenv("SIMLI_API_KEY", "").strip()
    simli_face_id = os.getenv("SIMLI_FACE_ID", "").strip()
    openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip()
    deepgram_stt_model = os.getenv("LIVEKIT_DEEPGRAM_STT_MODEL", "nova-3").strip()
    deepgram_tts_model = os.getenv(
        "LIVEKIT_DEEPGRAM_TTS_MODEL", "aura-2-asteria-en"
    ).strip()

    if not simli_api_key:
        raise ValueError("SIMLI_API_KEY is missing.")
    if not simli_face_id:
        raise ValueError("SIMLI_FACE_ID is missing.")
    if not os.getenv("OPENROUTER_API_KEY", "").strip():
        raise ValueError("OPENROUTER_API_KEY is missing.")
    if not os.getenv("DEEPGRAM_API_KEY", "").strip():
        raise ValueError("DEEPGRAM_API_KEY is missing.")

    await ctx.connect()
    participant = await ctx.wait_for_participant()
    scenario = participant.attributes.get("scenario", "Customer success escalation")
    persona_name = participant.attributes.get("persona_name", "Jordan")
    persona_goal = participant.attributes.get(
        "persona_goal", "Act like the customer or stakeholder in the scenario."
    )
    environment = participant.attributes.get("environment", "Escalation call")
    instructions = _build_instructions(
        base_instructions=base_instructions,
        scenario=scenario,
        persona_name=persona_name,
        persona_goal=persona_goal,
        environment=environment,
    )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(
            model=deepgram_stt_model,
        ),
        llm=openai.LLM.with_openrouter(
            model=openrouter_model,
            app_name="AI Roleplay Studio",
            site_url="http://localhost:8501",
        ),
        tts=deepgram.TTS(
            model=deepgram_tts_model,
        ),
    )

    avatar = simli.AvatarSession(
        simli_config=simli.SimliConfig(
            api_key=simli_api_key,
            face_id=simli_face_id,
        ),
    )

    await avatar.start(session, room=ctx.room)

    await session.start(
        agent=Agent(instructions=instructions),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name=os.getenv("LIVEKIT_AGENT_NAME", DEFAULT_AGENT_NAME),
        )
    )
