import os
import requests

# ElevenLabs API settings
API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "Mg1264PmwVoIedxsF9nu"

# Generate excited shout for a given name using ElevenLabs API
def generate_name(name):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"Content-Type": "application/json", "xi-api-key": API_KEY}
    data = {
        "text": f"{name.upper()}!!",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.3,
            "similarity_boost": 0.8,
            "style": 1
        }
    }
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        os.makedirs("temp_audio", exist_ok=True)
        output_file = f"temp_audio/{name}.mp3"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return output_file
    else:
        print(f"Error generating audio for {name}: {response.text}")
        return None

def generate_happy_birthday(name):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"Content-Type": "application/json", "xi-api-key": API_KEY}
    data = {
        "text": f"HAPPY BIRTHDAY {name.upper()}!!",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.3,
            "similarity_boost": 1,
            "style": 0.5
        }
    }
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        os.makedirs("temp_audio", exist_ok=True)
        output_file = f"temp_audio/{name}_happy.mp3"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return output_file
    else:
        print(f"Error generating audio for {name}: {response.text}")
        return None