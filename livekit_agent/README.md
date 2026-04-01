# LiveKit + Simli Agent Scaffold

This folder contains a persistent-session `LiveKit + Simli` agent scaffold using your preferred voice stack:

- Deepgram for speech-to-text
- OpenRouter for the LLM
- Deepgram for text-to-speech
- Simli for the avatar
- LiveKit for the continuous realtime room/session

## Why This Exists

Your earlier browser-only flow manually coordinated mic capture, silence detection, STT, LLM, TTS, and avatar playback turn by turn. That works for demos, but it is more fragile for a long-running realtime session.

This LiveKit path keeps the conversation inside one persistent room so the avatar can feel more like an always-present call participant.

## What This Agent Does

- creates a LiveKit agent worker
- starts a persistent `AgentSession`
- starts a Simli avatar session attached to the same room
- uses `Silero VAD + Deepgram STT + OpenRouter LLM + Deepgram TTS`

## How The Voice Pipeline Works

1. The browser joins a LiveKit room and publishes the user's microphone.
2. LiveKit streams the audio to the agent worker.
3. Silero VAD helps determine when the user is actively speaking.
4. Deepgram transcribes the utterance.
5. OpenRouter generates the in-character reply.
6. Deepgram synthesizes the reply audio.
7. Simli turns that reply into the avatar's live audio/video output in the same room.
8. The frontend simply stays connected and renders the remote avatar stream.

## Required Environment Variables

Add these to your main `.env`:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

DEEPGRAM_API_KEY=your_deepgram_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini

SIMLI_API_KEY=your_simli_api_key
SIMLI_FACE_ID=your_simli_face_id

LIVEKIT_AGENT_INSTRUCTIONS=You are a roleplay training partner. Stay in character and respond naturally.

LIVEKIT_DEEPGRAM_STT_MODEL=nova-3
LIVEKIT_DEEPGRAM_TTS_MODEL=aura-2-asteria-en
```

## Dependencies

Install the LiveKit-specific packages:

```powershell
python -m pip install -r livekit_agent/requirements-livekit.txt
```

## Run The Agent

```powershell
python livekit_agent/agent.py dev
```

Or:

```powershell
python livekit_agent/agent.py start
```

The exact mode you use depends on your local LiveKit workflow.

## What To Do With LiveKit

1. Create a LiveKit Cloud account.
2. Create a Video Conference sandbox/project.
3. Copy:
   `LIVEKIT_URL`
   `LIVEKIT_API_KEY`
   `LIVEKIT_API_SECRET`
4. Put those values in `.env` together with your `DEEPGRAM_API_KEY`, `OPENROUTER_API_KEY`, and Simli values.
5. Install the agent dependencies.
6. Run the LiveKit agent worker from this folder.
7. Join the LiveKit room from the Streamlit client or LiveKit playground.

## Next Recommended Step

Once this agent is running, the next step is to replace the current custom Streamlit browser-side turn loop with a proper LiveKit room client.

That is the change that gives you the "whole active session" feel you asked for.
