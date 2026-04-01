from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="AI Roleplay Studio", page_icon="AI", layout="wide")

DEFAULT_BACKEND_URL = "http://localhost:8000"
DEFAULT_ROOM_NAME = "roleplay-room"


def component(
    backend_url: str,
    room_name: str,
    participant_name: str,
    scenario: str,
    persona_name: str,
    persona_goal: str,
    environment_label: str,
) -> None:
    payload = json.dumps(
        {
            "backendUrl": backend_url,
            "roomName": room_name,
            "participantName": participant_name,
            "scenario": scenario,
            "personaName": persona_name,
            "personaGoal": persona_goal,
            "environment": environment_label,
        }
    )
    html = f"""
    <div style="font-family:Arial,sans-serif;color:#173630;">
      <div style="display:grid;grid-template-columns:1.25fr .75fr;gap:18px;">
        <section style="background:#0e2624;border-radius:28px;padding:18px;min-height:760px;position:relative;overflow:hidden;">
          <div style="position:absolute;inset:0;background:radial-gradient(circle at top right, rgba(244,210,143,.14), transparent 28%);"></div>
          <div style="position:relative;z-index:1;display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <div>
              <div style="color:#fff;font-size:12px;letter-spacing:.12em;text-transform:uppercase;opacity:.78;">Live Session</div>
              <div style="color:#fff;font-size:24px;font-weight:800;margin-top:6px;">Avatar Stage</div>
            </div>
            <div style="display:flex;gap:10px;">
              <button id="joinBtn" style="border:none;background:#f4d28f;color:#12332f;padding:12px 16px;border-radius:999px;font-weight:800;cursor:pointer;">Join Session</button>
              <button id="leaveBtn" style="border:none;background:rgba(255,255,255,.12);color:#fff;padding:12px 16px;border-radius:999px;font-weight:700;cursor:pointer;">Leave</button>
              <button id="fullscreenBtn" style="border:none;background:rgba(255,255,255,.12);color:#fff;padding:12px 16px;border-radius:999px;font-weight:700;cursor:pointer;">Fullscreen</button>
            </div>
          </div>
          <div id="stageWrap" style="position:relative;z-index:1;height:650px;border-radius:24px;overflow:hidden;background:#091917;border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center;">
            <video id="remoteVideo" autoplay playsinline style="width:100%;height:100%;object-fit:cover;background:#091917;"></video>
            <audio id="remoteAudio" autoplay style="display:none;"></audio>
            <div id="placeholder" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;text-align:center;padding:24px;">
              <div>
                <div style="font-size:66px;">AI</div>
                <div style="font-size:28px;font-weight:800;margin-top:10px;">Waiting For Session</div>
                <div style="font-size:14px;line-height:1.7;color:rgba(255,255,255,.75);margin-top:8px;">Join the LiveKit room to start a persistent Simli conversation.</div>
              </div>
            </div>
            <div id="statusBar" style="position:absolute;left:18px;right:18px;top:18px;display:flex;justify-content:space-between;gap:12px;">
              <div id="statusChip" style="background:rgba(9,18,17,.62);color:#fff;padding:10px 14px;border-radius:999px;font-size:13px;font-weight:700;backdrop-filter:blur(10px);">Idle</div>
              <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <div style="background:rgba(9,18,17,.5);color:#fff;padding:10px 14px;border-radius:999px;font-size:12px;backdrop-filter:blur(10px);">Room <span id="roomLabel"></span></div>
                <div style="background:rgba(9,18,17,.5);color:#fff;padding:10px 14px;border-radius:999px;font-size:12px;backdrop-filter:blur(10px);">You <span id="participantLabel"></span></div>
              </div>
            </div>
          </div>
          <div style="position:relative;z-index:1;display:flex;justify-content:center;margin-top:18px;">
            <div style="display:flex;gap:12px;align-items:center;background:rgba(9,18,17,.72);border:1px solid rgba(255,255,255,.08);padding:12px 14px;border-radius:999px;backdrop-filter:blur(12px);">
              <button id="muteBtn" style="border:none;background:rgba(255,255,255,.12);color:#fff;padding:12px 16px;border-radius:999px;font-weight:700;cursor:pointer;">Mute Mic</button>
              <button id="chatToggleBtn" style="border:none;background:rgba(255,255,255,.12);color:#fff;padding:12px 16px;border-radius:999px;font-weight:700;cursor:pointer;">Hide Transcript</button>
            </div>
          </div>
        </section>

        <aside id="chatPanel" style="background:#fff;border:1px solid rgba(0,0,0,.06);border-radius:28px;padding:18px;height:760px;box-shadow:0 18px 50px rgba(0,0,0,.05);display:flex;flex-direction:column;overflow:hidden;">
          <div style="padding:18px;border-radius:20px;background:#f5f7f6;border:1px solid rgba(16,54,48,.08);margin-bottom:14px;">
            <div style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#6b837b;">Session Context</div>
            <div style="margin-top:12px;display:grid;gap:10px;">
              <div><div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#789089;">Scenario</div><div id="scenarioLabel" style="font-size:15px;font-weight:700;color:#173630;margin-top:2px;"></div></div>
              <div><div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#789089;">Persona</div><div id="personaLabel" style="font-size:15px;font-weight:700;color:#173630;margin-top:2px;"></div></div>
              <div><div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#789089;">Environment</div><div id="environmentLabel" style="font-size:15px;font-weight:700;color:#173630;margin-top:2px;"></div></div>
              <div><div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#789089;">Goal</div><div id="goalLabel" style="font-size:14px;line-height:1.6;color:#45615a;margin-top:2px;"></div></div>
            </div>
          </div>
          <div style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#6b837b;">Transcript</div>
          <div style="font-size:22px;font-weight:800;margin-top:4px;margin-bottom:12px;">Conversation</div>
          <div id="chatList" style="flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;display:flex;flex-direction:column;gap:12px;padding-right:6px;scrollbar-width:auto;">
            <div id="emptyState" style="padding:20px;border-radius:18px;background:#f4f7f6;color:#5c766f;line-height:1.7;">Join the session to start receiving LiveKit transcriptions from both you and the agent.</div>
          </div>
        </aside>
      </div>
    </div>

    <script type="module">
      import {{ Room, RoomEvent, Track, createLocalAudioTrack }} from "https://esm.sh/livekit-client";

      const config = {payload};
      const joinBtn = document.getElementById("joinBtn");
      const leaveBtn = document.getElementById("leaveBtn");
      const fullscreenBtn = document.getElementById("fullscreenBtn");
      const muteBtn = document.getElementById("muteBtn");
      const chatToggleBtn = document.getElementById("chatToggleBtn");
      const statusChip = document.getElementById("statusChip");
      const roomLabel = document.getElementById("roomLabel");
      const participantLabel = document.getElementById("participantLabel");
      let remoteVideo = document.getElementById("remoteVideo");
      let remoteAudio = document.getElementById("remoteAudio");
      const placeholder = document.getElementById("placeholder");
      const stageWrap = document.getElementById("stageWrap");
      const chatPanel = document.getElementById("chatPanel");
      const chatList = document.getElementById("chatList");
      const emptyState = document.getElementById("emptyState");
      const scenarioLabel = document.getElementById("scenarioLabel");
      const personaLabel = document.getElementById("personaLabel");
      const environmentLabel = document.getElementById("environmentLabel");
      const goalLabel = document.getElementById("goalLabel");
      const feedbackCard = document.createElement("div");
      feedbackCard.style.marginTop = "14px";
      feedbackCard.style.padding = "16px";
      feedbackCard.style.borderRadius = "18px";
      feedbackCard.style.background = "#f5f7f6";
      feedbackCard.style.border = "1px solid rgba(16,54,48,.08)";
      feedbackCard.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
          <div>
            <div style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#6b837b;">Overall Feedback</div>
            <div style="font-size:14px;color:#5c766f;margin-top:6px;">Use the full stored session to evaluate the conversation.</div>
          </div>
          <button id="feedbackBtn" style="border:none;background:#173630;color:#fff;padding:10px 14px;border-radius:999px;font-weight:700;cursor:pointer;">Generate</button>
        </div>
        <div id="feedbackBody" style="display:none;margin-top:14px;color:#173630;"></div>
      `;
      chatPanel.appendChild(feedbackCard);
      const feedbackBtn = document.getElementById("feedbackBtn");
      const feedbackBody = document.getElementById("feedbackBody");

      roomLabel.textContent = config.roomName;
      participantLabel.textContent = config.participantName;
      scenarioLabel.textContent = config.scenario;
      personaLabel.textContent = config.personaName;
      environmentLabel.textContent = config.environment;
      goalLabel.textContent = config.personaGoal;

      let room = null;
      let localAudioTrack = null;
      let activeRoomName = "";
      const transcriptSegments = new Map();
      const persistedSegmentIds = new Set();
      let remoteSpeaking = false;

      const setStatus = (text) => {{
        statusChip.textContent = text;
      }};

      const setListeningState = () => {{
        if (!room) {{
          setStatus("Idle");
          return;
        }}
        setStatus(remoteSpeaking ? "Avatar Speaking" : "Listening");
      }};

      const initSessionStore = async () => {{
        const response = await fetch(`${{config.backendUrl}}/session/init`, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{
            room_name: activeRoomName,
            participant_name: config.participantName,
            scenario: config.scenario,
            persona_name: config.personaName,
            persona_goal: config.personaGoal,
            environment: config.environment,
          }}),
        }});
        const data = await response.json().catch(() => ({{}}));
        if (!response.ok) {{
          throw new Error(data.detail || "Failed to initialize session storage.");
        }}
      }};

      const escapeHtml = (text) =>
        text
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#39;");

      const renderTranscripts = () => {{
        const items = Array.from(transcriptSegments.values()).sort(
          (a, b) => (a.firstReceivedTime || 0) - (b.firstReceivedTime || 0)
        );

        if (!items.length) {{
          emptyState.style.display = "block";
          return;
        }}

        emptyState.style.display = "none";
        chatList.querySelectorAll("[data-segment='true']").forEach((node) => node.remove());

        for (const segment of items) {{
          const wrapper = document.createElement("div");
          const fromUser = (segment.speaker || "").toLowerCase() === config.participantName.toLowerCase();
          wrapper.setAttribute("data-segment", "true");
          wrapper.style.padding = "16px";
          wrapper.style.borderRadius = "18px";
          wrapper.style.background = fromUser ? "#173630" : "#f4f7f6";
          wrapper.style.color = fromUser ? "#fff" : "#173630";
          wrapper.style.alignSelf = fromUser ? "flex-end" : "stretch";
          wrapper.style.maxWidth = "92%";
          wrapper.style.boxShadow = fromUser ? "0 12px 32px rgba(23,54,48,.18)" : "none";
          wrapper.innerHTML = `
            <div style="font-size:11px;letter-spacing:.08em;text-transform:uppercase;opacity:.72;">${{escapeHtml(segment.speakerLabel)}}</div>
            <div style="margin-top:6px;line-height:1.6;font-size:14px;">${{escapeHtml(segment.text)}}</div>
          `;
          chatList.appendChild(wrapper);
        }}

        chatList.scrollTop = chatList.scrollHeight;
      }};

      const persistSegment = async (segment) => {{
        try {{
          await fetch(`${{config.backendUrl}}/session/segment`, {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{
              room_name: activeRoomName,
              segment,
            }}),
          }});
        }} catch (error) {{
          console.error("Failed to persist transcript segment", error);
        }}
      }};

      const deleteSessionStore = async () => {{
        if (!activeRoomName) return;
        try {{
          await fetch(`${{config.backendUrl}}/session/${{encodeURIComponent(activeRoomName)}}`, {{
            method: "DELETE",
          }});
        }} catch (error) {{
          console.error("Failed to delete session storage", error);
        }}
      }};

      const bindRemoteAudioState = (element) => {{
        element.addEventListener("play", () => {{
          remoteSpeaking = true;
          setStatus("Avatar Speaking");
        }});
        element.addEventListener("playing", () => {{
          remoteSpeaking = true;
          setStatus("Avatar Speaking");
        }});
        element.addEventListener("pause", () => {{
          remoteSpeaking = false;
          setListeningState();
        }});
        element.addEventListener("ended", () => {{
          remoteSpeaking = false;
          setListeningState();
        }});
      }};

      const renderFeedback = (payload) => {{
        feedbackBody.style.display = "block";
        feedbackBody.innerHTML = `
          <div style="display:grid;grid-template-columns:repeat(4, minmax(0, 1fr));gap:10px;margin-bottom:12px;">
            <div style="padding:12px;border-radius:14px;background:#fff;"><div style="font-size:11px;color:#789089;text-transform:uppercase;">Clarity</div><div style="font-size:22px;font-weight:800;margin-top:4px;">${{payload.scores.clarity}}</div></div>
            <div style="padding:12px;border-radius:14px;background:#fff;"><div style="font-size:11px;color:#789089;text-transform:uppercase;">Relevance</div><div style="font-size:22px;font-weight:800;margin-top:4px;">${{payload.scores.relevance}}</div></div>
            <div style="padding:12px;border-radius:14px;background:#fff;"><div style="font-size:11px;color:#789089;text-transform:uppercase;">Confidence</div><div style="font-size:22px;font-weight:800;margin-top:4px;">${{payload.scores.confidence}}</div></div>
            <div style="padding:12px;border-radius:14px;background:#fff;"><div style="font-size:11px;color:#789089;text-transform:uppercase;">Overall</div><div style="font-size:22px;font-weight:800;margin-top:4px;">${{payload.scores.overall}}</div></div>
          </div>
          <div style="padding:14px;border-radius:14px;background:#fff;line-height:1.6;">
            <div style="font-size:11px;color:#789089;text-transform:uppercase;">Summary</div>
            <div style="margin-top:6px;">${{escapeHtml(payload.summary || "")}}</div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;">
            <div style="padding:14px;border-radius:14px;background:#fff;">
              <div style="font-size:11px;color:#789089;text-transform:uppercase;">Strengths</div>
              <div style="margin-top:6px;line-height:1.7;">${{(payload.strengths || []).map((item) => `• ${{escapeHtml(item)}}`).join("<br>")}}</div>
            </div>
            <div style="padding:14px;border-radius:14px;background:#fff;">
              <div style="font-size:11px;color:#789089;text-transform:uppercase;">Improvements</div>
              <div style="margin-top:6px;line-height:1.7;">${{(payload.improvements || []).map((item) => `• ${{escapeHtml(item)}}`).join("<br>")}}</div>
            </div>
          </div>
        `;
      }};

      const updateTranscriptions = (segments, participant) => {{
        const speaker = participant?.identity || "agent";
        const speakerLabel = participant?.name || participant?.identity || "Agent";
        for (const segment of segments) {{
          transcriptSegments.set(segment.id, {{
            ...segment,
            speaker,
            speakerLabel,
          }});
          if (segment.final && !persistedSegmentIds.has(segment.id) && segment.text?.trim()) {{
            persistedSegmentIds.add(segment.id);
            persistSegment({{
              segment_id: segment.id,
              speaker_identity: speaker,
              speaker_label: speakerLabel,
              text: segment.text.trim(),
              is_final: true,
              first_received_time: segment.firstReceivedTime || 0,
            }});
            if ((speaker || "").toLowerCase() === config.participantName.toLowerCase()) {{
              setStatus("Generating");
            }} else {{
              remoteSpeaking = true;
              setStatus("Avatar Speaking");
            }}
          }}
        }}
        renderTranscripts();
      }};

      const attachExistingTracks = () => {{
        if (!room) return;
        for (const participant of room.remoteParticipants.values()) {{
          for (const publication of participant.trackPublications.values()) {{
            if (publication.track) {{
              attachTrack(publication.track);
            }}
          }}
        }}
      }};

      const makeSessionRoomName = () => {{
        const base = (config.roomName || "roleplay-room")
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9-_]/g, "-")
          .replace(/-+/g, "-")
          .replace(/^-|-$/g, "") || "roleplay-room";
        const suffix = `${{Date.now()}}-${{Math.random().toString(36).slice(2, 8)}}`;
        return `${{base}}-${{suffix}}`;
      }};

      const attachTrack = (track) => {{
        placeholder.style.display = "none";
        if (track.kind === Track.Kind.Video) {{
          const element = track.attach();
          remoteVideo.replaceWith(element);
          remoteVideo = element;
          remoteVideo.id = "remoteVideo";
          remoteVideo.setAttribute("playsinline", "true");
          remoteVideo.autoplay = true;
          element.style.width = "100%";
          element.style.height = "100%";
          element.style.objectFit = "cover";
        }}
        if (track.kind === Track.Kind.Audio) {{
          const element = track.attach();
          remoteAudio.replaceWith(element);
          remoteAudio = element;
          remoteAudio.id = "remoteAudio";
          remoteAudio.autoplay = true;
          remoteAudio.style.display = "none";
          bindRemoteAudioState(remoteAudio);
        }}
      }};

      const createRoom = async () => {{
        activeRoomName = makeSessionRoomName();
        roomLabel.textContent = activeRoomName;
        const tokenRes = await fetch(`${{config.backendUrl}}/livekit/token`, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{
            room_name: activeRoomName,
            participant_name: config.participantName,
            scenario: config.scenario,
            persona_name: config.personaName,
            persona_goal: config.personaGoal,
            environment: config.environment,
          }}),
        }});
        const tokenData = await tokenRes.json();
        if (!tokenRes.ok) {{
          activeRoomName = "";
          roomLabel.textContent = config.roomName;
          throw new Error(tokenData.detail || "Failed to create LiveKit token.");
        }}

        await initSessionStore();
        room = new Room();
        room.on(RoomEvent.TrackSubscribed, (track) => attachTrack(track));
        room.on(RoomEvent.Disconnected, () => setStatus("Disconnected"));
        room.on(RoomEvent.ConnectionStateChanged, (state) => setStatus(state));
        room.on(RoomEvent.TranscriptionReceived, updateTranscriptions);

        await room.connect(tokenData.livekit_url, tokenData.token);
        localAudioTrack = await createLocalAudioTrack({{
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }});
        await room.localParticipant.publishTrack(localAudioTrack);
        attachExistingTracks();
        remoteSpeaking = false;
        setStatus("Listening");
      }};

      joinBtn.onclick = async () => {{
        try {{
          if (room) return;
          setStatus("Connecting");
          await createRoom();
        }} catch (error) {{
          setStatus(error instanceof Error ? error.message : String(error));
        }}
      }};

      leaveBtn.onclick = async () => {{
        if (localAudioTrack) {{
          await localAudioTrack.stop();
          localAudioTrack = null;
        }}
        if (room) {{
          room.off(RoomEvent.TranscriptionReceived, updateTranscriptions);
          await room.disconnect();
          room = null;
        }}
        await deleteSessionStore();
        remoteSpeaking = false;
        placeholder.style.display = "flex";
        persistedSegmentIds.clear();
        transcriptSegments.clear();
        chatList.querySelectorAll("[data-segment='true']").forEach((node) => node.remove());
        emptyState.style.display = "block";
        feedbackBody.style.display = "none";
        feedbackBody.innerHTML = "";
        remoteVideo.replaceWith(remoteVideo.cloneNode(false));
        remoteAudio.replaceWith(remoteAudio.cloneNode(false));
        remoteVideo = document.getElementById("remoteVideo") || remoteVideo;
        remoteAudio = document.getElementById("remoteAudio") || remoteAudio;
        roomLabel.textContent = config.roomName;
        activeRoomName = "";
        setStatus("Idle");
      }};

      muteBtn.onclick = async () => {{
        if (!localAudioTrack) return;
        if (localAudioTrack.isMuted) {{
          await localAudioTrack.unmute();
          muteBtn.textContent = "Mute Mic";
        }} else {{
          await localAudioTrack.mute();
          muteBtn.textContent = "Unmute Mic";
        }}
      }};

      chatToggleBtn.onclick = () => {{
        const visible = chatPanel.style.display !== "none";
        chatPanel.style.display = visible ? "none" : "flex";
        chatToggleBtn.textContent = visible ? "Show Transcript" : "Hide Transcript";
      }};

      feedbackBtn.onclick = async () => {{
        try {{
          if (!activeRoomName) {{
            throw new Error("Join a session first.");
          }}
          feedbackBtn.disabled = true;
          feedbackBtn.textContent = "Generating...";
          const response = await fetch(`${{config.backendUrl}}/session/${{encodeURIComponent(activeRoomName)}}/evaluate`, {{
            method: "POST",
          }});
          const data = await response.json();
          if (!response.ok) {{
            throw new Error(data.detail || "Failed to generate session feedback.");
          }}
          renderFeedback(data);
        }} catch (error) {{
          feedbackBody.style.display = "block";
          feedbackBody.innerHTML = `<div style="padding:14px;border-radius:14px;background:#fff3f0;color:#8a3d2f;">${{escapeHtml(error instanceof Error ? error.message : String(error))}}</div>`;
        }} finally {{
          feedbackBtn.disabled = false;
          feedbackBtn.textContent = "Generate";
        }}
      }};

      fullscreenBtn.onclick = async () => {{
        try {{
          if (!document.fullscreenElement) await stageWrap.requestFullscreen();
          else await document.exitFullscreen();
        }} catch (error) {{
          setStatus("Fullscreen blocked");
        }}
      }};
    </script>
    """
    components.html(html, height=860)


st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f3efe6 0%, #eef5f3 100%); }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1500px; }
    section[data-testid="stSidebar"] { background: #173630; }
    section[data-testid="stSidebar"] * { color: #f4f1ea !important; }
    div[data-testid="stTextInput"] input {
      background: rgba(255,255,255,.08) !important;
      border-radius: 14px !important;
      border: 1px solid rgba(255,255,255,.08) !important;
    }
    iframe[title="streamlit_components.v1.html"] ::-webkit-scrollbar {
      width: 10px;
    }
    iframe[title="streamlit_components.v1.html"] ::-webkit-scrollbar-thumb {
      background: rgba(23,54,48,.28);
      border-radius: 999px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("AI Roleplay Studio")
st.caption("Persistent-session LiveKit + Simli room client.")

with st.sidebar:
    st.header("Session")
    backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND_URL)
    room_name = st.text_input("Room Name", value=DEFAULT_ROOM_NAME)
    participant_name = st.text_input("Participant Name", value="user")
    scenario = st.text_input("Scenario", value="Customer success escalation")
    persona_name = st.text_input("Persona Name", value="Jordan")
    persona_goal = st.text_area(
        "Persona Goal",
        value="Act like a frustrated customer whose issue is affecting their team.",
        height=120,
    )
    environment_label = st.text_input("Environment", value="Escalation call")
    st.caption("LiveKit credentials and the Simli face are taken from the backend environment.")

component(
    backend_url=backend_url,
    room_name=room_name,
    participant_name=participant_name,
    scenario=scenario,
    persona_name=persona_name,
    persona_goal=persona_goal,
    environment_label=environment_label,
)
