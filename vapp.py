from fastapi import FastAPI, WebSocket
import os
import openai
import deepgram
from twilio.twiml.voice_response import VoiceResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa"}

# Handle Twilio Calls
@app.post("/incoming-call")
async def handle_call():
    response = VoiceResponse()
    response.say("Connecting you to the AI assistant.")
    return str(response)

# Handle WebSockets for Deepgram STT
@app.websocket("/stt-stream")
async def stt_websocket(websocket: WebSocket):
    await websocket.accept()
    deepgram_client = deepgram.Deepgram(os.getenv("DEEPGRAM_API_KEY"))
    async for message in websocket.iter_text():
        transcript = deepgram_client.transcribe(message)  # Simulated transcription
        response = get_grok_response(transcript)
        await websocket.send_text(response)
#test comment
# Call Grok API
def get_grok_response(text):
    grok_api_key = os.getenv("GROK_API_KEY")
    response = openai.ChatCompletion.create(
        model="grok-1",
        messages=[{"role": "system", "content": text}],
        api_key=grok_api_key
    )
    return response["choices"][0]["message"]["content"]

# Convert LLM Response to Speech using Azure TTS
def text_to_speech(text):
    from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
    speech_config = SpeechConfig(subscription=os.getenv("AZURE_TTS_KEY"), region="eastus")
    synthesizer = SpeechSynthesizer(speech_config=speech_config)
    synthesizer.speak_text_async(text)
    
    