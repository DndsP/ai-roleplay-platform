import requests

# 🔑 Replace with your Deepgram API Key
DEEPGRAM_API_KEY = "1cf27414056e404883f840d3e5d053292fe0ed45"

# 🎵 Path to your audio file (wav/mp3/flac recommended)
AUDIO_FILE_PATH = "sample-0.mp3"

# 📡 Deepgram endpoint
url = "https://api.deepgram.com/v1/listen"

headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "audio/wav"  # change if using mp3/flac
}

# 📂 Read audio file
with open(AUDIO_FILE_PATH, "rb") as audio:
    response = requests.post(url, headers=headers, data=audio)

# 📊 Print response
if response.status_code == 200:
    result = response.json()
    transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
    
    print("\n✅ Transcription:")
    print(transcript)
else:
    print("\n❌ Error:", response.status_code)
    print(response.text)