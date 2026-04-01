# Session Data

This document explains what session data exists in the current project, where it lives, and when it is deleted.

## Session Memory Model

The project currently has two layers of temporary session state:

1. frontend UI state
2. backend session transcript storage

It does not yet use a vector database.

## 1. Frontend UI State

File:

- [frontend/app.py](c:/Users/SuryaD/Desktop/AI_Roleplay/frontend/app.py)

What the frontend keeps in memory during a page load:

- backend URL
- base room name
- participant name
- scenario
- persona name
- persona goal
- environment
- active room name after join
- current transcript messages shown in the chat panel
- current feedback card result
- current connection/status state

Important detail:

- the frontend base room name is only a prefix
- the actual active room name is generated at join time

Example:

- sidebar room name: `roleplay-room`
- actual session room name: `roleplay-room-1711880000000-ab12cd`

## 2. Backend Session Storage

File:

- [backend/app/services/session_store.py](c:/Users/SuryaD/Desktop/AI_Roleplay/backend/app/services/session_store.py)

Storage location:

- `session_data/`

Each active session is stored as a JSON file named from the room.

Example:

- `session_data/roleplay-room-1711880000000-ab12cd.json`

## Stored Session Shape

Each session file stores:

- `context`
- `transcript_segments`

### `context`

Fields:

- `room_name`
- `participant_name`
- `scenario`
- `persona_name`
- `persona_goal`
- `environment`

### `transcript_segments`

Each segment stores:

- `segment_id`
- `speaker_identity`
- `speaker_label`
- `text`
- `is_final`
- `first_received_time`

Example:

```json
{
  "context": {
    "room_name": "roleplay-room-1711880000000-ab12cd",
    "participant_name": "user",
    "scenario": "Customer success escalation",
    "persona_name": "Jordan",
    "persona_goal": "Act like a frustrated customer whose issue is affecting their team.",
    "environment": "Escalation call"
  },
  "transcript_segments": [
    {
      "segment_id": "seg-1",
      "speaker_identity": "user",
      "speaker_label": "user",
      "text": "Can you walk me through the escalation timeline?",
      "is_final": true,
      "first_received_time": 1711880000.25
    },
    {
      "segment_id": "seg-2",
      "speaker_identity": "roleplay-agent",
      "speaker_label": "Jordan",
      "text": "This issue has already delayed my team twice this week.",
      "is_final": true,
      "first_received_time": 1711880004.12
    }
  ]
}
```

## When Session Data Is Created

When the user clicks `Join Session`:

1. the frontend generates a new active room name
2. the frontend calls `POST /session/init`
3. the backend creates a new JSON file for that room

## When Transcript Data Is Added

During the live session:

1. LiveKit emits transcription events
2. the frontend receives those transcript segments
3. final segments are sent to `POST /session/segment`
4. the backend appends them to the session JSON file

Only final transcript segments are stored.

## When Session Data Is Read

The project reads backend session data in two main cases:

### Overall Session Evaluation

Endpoint:

- `POST /session/{room_name}/evaluate`

Purpose:

- evaluate the full interview, sales call, or roleplay using all stored transcript segments

### Session Inspection

Endpoint:

- `GET /session/{room_name}`

Purpose:

- fetch the stored session document for debugging or review

## When Session Data Is Deleted

When the user clicks `Leave`:

1. the frontend disconnects from the LiveKit room
2. the frontend calls `DELETE /session/{room_name}`
3. the backend deletes that session JSON file

This means:

- old session transcript memory does not remain for future joins
- the next join starts clean
- one session cannot read another session's stored memory

## Session Isolation Rule

The current system is explicitly designed for per-session isolation:

- each join creates a new active room
- each room gets its own backend session file
- each leave deletes that file

So:

- session A does not share transcript memory with session B
- rejoining creates a new room and a new storage file

## What The Agent Uses As Memory

There are two different kinds of memory in the current project:

### Live Conversation Memory

Inside the LiveKit agent:

- the voice/LLM session carries the ongoing conversational context while the room is active

### Stored Session Memory

On the backend:

- the transcript segments are stored so the entire session can be evaluated later in the same active session window

The backend file store is not what drives the live reply generation turn by turn.

Instead:

- the agent handles live context in the room
- the backend file store supports session review and overall evaluation

## Not Yet Implemented

The following are not part of the current storage model yet:

- vector database memory
- long-term cross-session user memory
- permanent session archive after leave
- retrieval-augmented prompting from prior sessions

That can be added later, but the current project intentionally deletes session transcript storage after leave.
