# Workflow

This document explains how the current project works end to end.

## High-Level Architecture

There are 5 main pieces:

1. Streamlit UI
2. Embedded browser LiveKit client
3. FastAPI backend
4. LiveKit agent worker
5. External providers

## 1. Streamlit UI

File:

- [frontend/app.py](c:/Users/SuryaD/Desktop/AI_Roleplay/frontend/app.py)

What it does:

- renders the page and sidebar
- collects:
  - backend URL
  - base room name
  - participant name
  - scenario
  - persona name
  - persona goal
  - environment
- injects those values into the browser component

Important detail:

- the visible room name in the sidebar is only the base room prefix
- the actual active room is created dynamically when the user clicks `Join Session`

## 2. Browser LiveKit Client

The embedded HTML/JavaScript client inside [frontend/app.py](c:/Users/SuryaD/Desktop/AI_Roleplay/frontend/app.py) handles the live session.

What it does:

1. generates a new unique room name on every join
2. requests `/livekit/token`
3. requests `/session/init`
4. joins the LiveKit room
5. publishes local microphone audio
6. subscribes to remote avatar video/audio tracks
7. listens for LiveKit transcription events
8. stores final transcript segments to `/session/segment`
9. requests `/session/{room_name}/evaluate` when the user clicks `Generate`
10. requests `DELETE /session/{room_name}` on leave

What it shows:

- avatar stage
- room label
- participant label
- status chip:
  - `Idle`
  - `Connecting`
  - `Listening`
  - `Generating`
  - `Avatar Speaking`
- transcript panel
- session context panel
- overall feedback panel

## 3. FastAPI Backend

File:

- [backend/app/main.py](c:/Users/SuryaD/Desktop/AI_Roleplay/backend/app/main.py)

What it does:

- validates requests
- creates LiveKit tokens
- stores and retrieves session transcript data
- evaluates the full session transcript
- exposes utility STT/chat/TTS/Simli endpoints

### Backend Route Map

`GET /health`

- input: none
- output: service health status

`POST /livekit/token`

- input:
  - room name
  - participant name
  - scenario
  - persona name
  - persona goal
  - environment
- output:
  - LiveKit token
  - resolved room name
  - participant name
  - LiveKit URL

`POST /session/init`

- input:
  - room name
  - participant name
  - scenario
  - persona name
  - persona goal
  - environment
- output:
  - initialized session document

`POST /session/segment`

- input:
  - room name
  - one final transcript segment
- output:
  - updated session document

`GET /session/{room_name}`

- input:
  - room name
- output:
  - full stored session data

`POST /session/{room_name}/evaluate`

- input:
  - room name
- output:
  - session-wide coaching evaluation

`DELETE /session/{room_name}`

- input:
  - room name
- output:
  - deletion confirmation

## 4. LiveKit Agent Worker

File:

- [livekit_agent/agent.py](c:/Users/SuryaD/Desktop/AI_Roleplay/livekit_agent/agent.py)

What it does:

1. joins the room after explicit LiveKit dispatch
2. waits for the user participant
3. reads roleplay context from participant attributes:
   - scenario
   - persona name
   - persona goal
   - environment
4. builds the agent instructions dynamically
5. starts the voice pipeline:
   - Silero VAD
   - Deepgram STT
   - OpenRouter LLM
   - Deepgram TTS
6. starts the Simli avatar session in the same room

### Agent Input

Input source:

- participant attributes from the LiveKit token

Fields:

- `scenario`
- `persona_name`
- `persona_goal`
- `environment`

### Agent Output

Output to the room:

- avatar video track from Simli
- avatar audio track from TTS/Simli
- LiveKit transcription events

## 5. External Services

### Deepgram

Used in:

- [livekit_agent/agent.py](c:/Users/SuryaD/Desktop/AI_Roleplay/livekit_agent/agent.py)
- [backend/app/services/deepgram_service.py](c:/Users/SuryaD/Desktop/AI_Roleplay/backend/app/services/deepgram_service.py)

Input:

- user audio
- text for TTS

Output:

- STT transcript
- TTS audio stream

### OpenRouter

Used in:

- [livekit_agent/agent.py](c:/Users/SuryaD/Desktop/AI_Roleplay/livekit_agent/agent.py)
- [backend/app/services/openrouter_service.py](c:/Users/SuryaD/Desktop/AI_Roleplay/backend/app/services/openrouter_service.py)

Input:

- persona instructions
- conversation turns or session transcript

Output:

- persona reply
- overall session evaluation

### Simli

Used in:

- [livekit_agent/agent.py](c:/Users/SuryaD/Desktop/AI_Roleplay/livekit_agent/agent.py)
- [backend/app/services/simli_service.py](c:/Users/SuryaD/Desktop/AI_Roleplay/backend/app/services/simli_service.py)

Input:

- configured face id
- room-linked avatar session

Output:

- remote avatar video/audio in the room

### LiveKit

Used in:

- frontend room client
- backend token service
- LiveKit agent worker

Input:

- user room join request
- participant audio
- agent dispatch configuration

Output:

- room transport
- media tracks
- transcription events

## Full Join Flow

### Step 1

The user fills session context in the sidebar.

### Step 2

The user clicks `Join Session`.

### Step 3

The frontend creates a unique room name such as:

`roleplay-room-1711880000000-ab12cd`

### Step 4

The frontend calls `POST /livekit/token`.

### Step 5

The backend creates a token and attaches:

- participant attributes for session context
- explicit agent dispatch for the agent worker

### Step 6

The frontend calls `POST /session/init`.

### Step 7

The browser joins the LiveKit room and publishes the microphone.

### Step 8

The LiveKit worker is dispatched into that room.

### Step 9

The agent reads the participant attributes and behaves according to:

- scenario
- persona name
- persona goal
- environment

### Step 10

The agent responds through Simli avatar video/audio.

### Step 11

The frontend receives transcription events and displays them in the transcript panel.

### Step 12

Each final transcript segment is sent to `POST /session/segment`.

## Full Leave Flow

### Step 1

The user clicks `Leave`.

### Step 2

The frontend disconnects from the room.

### Step 3

The frontend calls `DELETE /session/{room_name}`.

### Step 4

The backend deletes the stored session file for that room.

### Step 5

The next join creates a new room and starts a fresh session with no memory from the previous one.

## Why Session Memory Is Temporary

The project currently uses a file-based session store for active-session memory only.

That means:

- the session transcript is available during the session
- the transcript can be evaluated as a whole
- the transcript is deleted on leave
- there is no vector database yet
- there is no long-term cross-session memory yet

## Utility Routes Outside The Main Live Flow

The backend still includes direct utility routes:

- `/speech-to-text`
- `/chat`
- `/evaluate`
- `/tts`
- `/simli/session-token`

These are useful for debugging, testing, or standalone service calls, but the main user-facing app path is now:

`Frontend -> LiveKit token -> LiveKit room -> LiveKit agent -> Simli avatar`
