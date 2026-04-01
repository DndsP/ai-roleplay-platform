# AI Roleplay Studio

AI Roleplay Studio is a full-stack voice roleplay system with:

- a FastAPI backend
- a Streamlit frontend
- a LiveKit room for realtime media transport
- a LiveKit agent worker
- Deepgram for speech-to-text and text-to-speech in the live agent
- OpenRouter for persona-driven replies and session evaluation
- Simli for the live avatar

The current project creates a fresh room every time the user clicks `Join Session`, stores that session's transcript on the backend while the session is active, and deletes the stored session when the user clicks `Leave`.

## What The User Experiences

1. The user opens the Streamlit app.
2. The user enters:
   - scenario
   - persona name
   - persona goal
   - environment
3. The user clicks `Join Session`.
4. The frontend creates a new unique LiveKit room for that join.
5. The backend mints a LiveKit token and explicitly dispatches the agent into that room.
6. The browser publishes the user's microphone to the room.
7. The agent listens, speaks as the configured persona, and Simli renders the avatar.
8. Transcript messages are shown in the transcript panel and stored for that session.
9. The user can generate overall session feedback from the stored transcript.
10. When the user clicks `Leave`, the frontend disconnects and deletes that session's stored backend memory.

## Project Structure

```text
AI_Roleplay/
|-- backend/
|   `-- app/
|       |-- core/
|       |   `-- config.py
|       |-- models/
|       |   `-- schemas.py
|       |-- services/
|       |   |-- azure_tts_service.py
|       |   |-- deepgram_service.py
|       |   |-- livekit_service.py
|       |   |-- openrouter_service.py
|       |   |-- session_store.py
|       |   `-- simli_service.py
|       `-- main.py
|-- frontend/
|   `-- app.py
|-- livekit_agent/
|   |-- agent.py
|   |-- README.md
|   `-- requirements-livekit.txt
|-- session_data/
|-- .env.example
|-- requirements.txt
|-- run_livekit_stack.ps1
|-- SESSION_DATA.md
`-- WORKFLOW.md
```

## Setup

1. Create a local environment file from the template:

```powershell
Copy-Item .env.example .env
```

2. Add your real API keys and LiveKit values to `.env`.

3. Start the whole stack:

```powershell
.\run_livekit_stack.ps1
```

From Git Bash:

```bash
powershell -ExecutionPolicy Bypass -File ./run_livekit_stack.ps1
```

The launcher script:

- creates `.venv` if needed
- installs backend/frontend dependencies
- installs LiveKit agent dependencies
- starts the FastAPI backend
- starts the LiveKit agent worker
- starts the Streamlit frontend

## Required Environment Variables

Core services:

- `DEEPGRAM_API_KEY`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `OPENROUTER_EVALUATOR_MODEL`
- `SIMLI_API_KEY`
- `SIMLI_FACE_ID`

LiveKit:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `LIVEKIT_AGENT_NAME`
- `LIVEKIT_DEFAULT_ROOM`

Optional tuning:

- `LIVEKIT_AGENT_INSTRUCTIONS`
- `LIVEKIT_DEEPGRAM_STT_MODEL`
- `LIVEKIT_DEEPGRAM_TTS_MODEL`

Legacy utility endpoints still available:

- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`
- `AZURE_SPEECH_VOICE`

## Runtime Components

### Frontend

File:

- [frontend/app.py](c:/Users/SuryaD/Desktop/AI_Roleplay/frontend/app.py)

Responsibilities:

- collect session context from the sidebar
- create a new isolated session on every join
- request a LiveKit token from the backend
- join the LiveKit room
- publish the local microphone
- render the remote avatar video and audio
- render transcript bubbles from LiveKit transcription events
- store final transcript segments on the backend
- request full-session evaluation from the backend
- delete the backend session store on leave

### Backend API

File:

- [backend/app/main.py](c:/Users/SuryaD/Desktop/AI_Roleplay/backend/app/main.py)

Responsibilities:

- validate frontend and utility API requests
- generate LiveKit room tokens
- initialize per-session storage
- append transcript segments to the session store
- evaluate the stored full session
- expose utility STT, chat, TTS, and Simli token routes

### LiveKit Agent

File:

- [livekit_agent/agent.py](c:/Users/SuryaD/Desktop/AI_Roleplay/livekit_agent/agent.py)

Responsibilities:

- wait for a user participant
- read session context from participant attributes
- build the persona prompt dynamically
- run the voice pipeline:
  - Silero VAD
  - Deepgram STT
  - OpenRouter LLM
  - Deepgram TTS
- attach Simli avatar output to the same room

## API Contracts

### `GET /health`

Purpose:

- health check

Input:

- none

Output:

```json
{ "status": "ok" }
```

### `POST /livekit/token`

Purpose:

- create a user token for a fresh LiveKit room and explicitly dispatch the roleplay agent

Input:

```json
{
  "room_name": "roleplay-room-123456",
  "participant_name": "user",
  "scenario": "Customer success escalation",
  "persona_name": "Jordan",
  "persona_goal": "Act like a frustrated customer whose issue is affecting their team.",
  "environment": "Escalation call"
}
```

Output:

```json
{
  "token": "livekit-jwt",
  "room_name": "roleplay-room-123456",
  "participant_name": "user",
  "livekit_url": "wss://your-project.livekit.cloud"
}
```

### `POST /session/init`

Purpose:

- create backend storage for the active session

Input:

```json
{
  "room_name": "roleplay-room-123456",
  "participant_name": "user",
  "scenario": "Customer success escalation",
  "persona_name": "Jordan",
  "persona_goal": "Act like a frustrated customer whose issue is affecting their team.",
  "environment": "Escalation call"
}
```

Output:

```json
{
  "context": {
    "room_name": "roleplay-room-123456",
    "participant_name": "user",
    "scenario": "Customer success escalation",
    "persona_name": "Jordan",
    "persona_goal": "Act like a frustrated customer whose issue is affecting their team.",
    "environment": "Escalation call"
  },
  "transcript_segments": []
}
```

### `POST /session/segment`

Purpose:

- append one final transcript segment to the active backend session

Input:

```json
{
  "room_name": "roleplay-room-123456",
  "segment": {
    "segment_id": "segment_1",
    "speaker_identity": "user",
    "speaker_label": "user",
    "text": "Can you explain the rollout timeline?",
    "is_final": true,
    "first_received_time": 1711880000.25
  }
}
```

Output:

- the full current session document, including all stored transcript segments

### `GET /session/{room_name}`

Purpose:

- fetch the currently stored session

Input:

- room name in the path

Output:

- the session context plus all stored transcript segments

### `POST /session/{room_name}/evaluate`

Purpose:

- evaluate the full stored session using OpenRouter

Input:

- room name in the path

Output:

```json
{
  "scores": {
    "clarity": 8,
    "relevance": 7,
    "confidence": 8,
    "overall": 8
  },
  "strengths": ["..."],
  "improvements": ["..."],
  "summary": "..."
}
```

### `DELETE /session/{room_name}`

Purpose:

- delete stored backend memory for that session

Input:

- room name in the path

Output:

```json
{
  "status": "deleted",
  "room_name": "roleplay-room-123456"
}
```

## Utility Endpoints Still Present

These routes are still implemented in the backend and can be used independently, even though the main live session path uses the LiveKit agent.

### `POST /speech-to-text`

Service used:

- Deepgram

Input:

- multipart form-data with `audio`

Output:

```json
{
  "transcript": "transcribed text",
  "duration_seconds": 3.42,
  "language": "en"
}
```

### `POST /chat`

Service used:

- OpenRouter

Input:

```json
{
  "transcript": "user text",
  "scenario": "Customer success escalation",
  "persona_name": "Jordan",
  "persona_goal": "Act like the customer or stakeholder in the scenario.",
  "conversation_history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

Output:

```json
{
  "response": "persona reply",
  "persona_name": "Jordan",
  "scenario": "Customer success escalation"
}
```

### `POST /evaluate`

Service used:

- OpenRouter

Input:

```json
{
  "transcript": "user response",
  "scenario": "Customer success escalation",
  "coaching_goal": "Be clear, empathetic, and solution-oriented."
}
```

Output:

```json
{
  "scores": {
    "clarity": 8,
    "relevance": 7,
    "confidence": 8,
    "overall": 8
  },
  "strengths": ["..."],
  "improvements": ["..."],
  "summary": "..."
}
```

### `POST /tts`

Service used:

- Azure Speech

Input:

```json
{
  "text": "reply text",
  "voice": "en-US-AvaMultilingualNeural"
}
```

Output:

- `audio/mpeg` stream

### `POST /simli/session-token`

Service used:

- Simli

Input:

```json
{
  "face_id": "optional-face-id"
}
```

Output:

```json
{
  "session_token": "simli-token",
  "face_id": "resolved-face-id"
}
```

## Session Isolation Rules

- each click on `Join Session` creates a new unique room name
- a fresh backend session store is created for that room
- that session does not reuse transcript memory from previous sessions
- clicking `Leave` deletes the stored backend session for that room

## More Detail

- Architecture and end-to-end flow: [WORKFLOW.md](c:/Users/SuryaD/Desktop/AI_Roleplay/WORKFLOW.md)
- Session data lifecycle: [SESSION_DATA.md](c:/Users/SuryaD/Desktop/AI_Roleplay/SESSION_DATA.md)
