# FIRST RUNNING CODE, INCLUDES STT, LLM AND TTS
# from fastapi import FastAPI, WebSocket
# import os
# import openai
# import deepgram
# from twilio.twiml.voice_response import VoiceResponse
# import uvicorn

# app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa"}

# # Handle Twilio Calls
# @app.post("/incoming-call")
# async def handle_call():
#     response = VoiceResponse()
#     response.say("Connecting you to the AI assistant.")
#     return str(response)

# # Handle WebSockets for Deepgram STT
# @app.websocket("/stt-stream")
# async def stt_websocket(websocket: WebSocket):
#     await websocket.accept()
#     deepgram_client = deepgram.Deepgram(os.getenv("DEEPGRAM_API_KEY"))
#     async for message in websocket.iter_text():
#         transcript = deepgram_client.transcribe(message)  # Simulated transcription
#         response = get_grok_response(transcript)
#         await websocket.send_text(response)
# #test comment
# # Call Grok API
# def get_grok_response(text):
#     grok_api_key = os.getenv("GROK_API_KEY")
#     response = openai.ChatCompletion.create(
#         model="grok-1",
#         messages=[{"role": "system", "content": text}],
#         api_key=grok_api_key
#     )
#     return response["choices"][0]["message"]["content"]

# # Convert LLM Response to Speech using Azure TTS
# def text_to_speech(text):
#     from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
#     speech_config = SpeechConfig(subscription=os.getenv("AZURE_TTS_KEY"), region="eastus")
#     synthesizer = SpeechSynthesizer(speech_config=speech_config)
#     synthesizer.speak_text_async(text)
    
    
    
from fastapi import FastAPI, WebSocket, Response
import os
import openai
import deepgram
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import uvicorn
from fastapi import Form

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Voice AI Agent Running"}


# ✅ Handle Incoming Twilio Calls
@app.post("/incoming-call")
async def handle_call():
    response = VoiceResponse()
    response.say("Connecting you to the AI assistant. Please speak after the beep.")
    response.pause(length=1)
    response.record(timeout=10, transcribe=True)  # Records user input
    # return str(response)
    return Response(content=str(response), media_type="application/xml")

# ✅ Initiate Outbound Call using Twilio
#added form after str
@app.post("/make-call")
async def make_call(to_phone_number: str = Form(...)):
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    call = client.calls.create(
        to=to_phone_number,
        from_=TWILIO_PHONE_NUMBER,
        url="https://echochet-azaqfbfhfvcgf5g2.eastus2-01.azurewebsites.net/incoming-call"  # Change to your deployed Azure webhook
    )

    return {"message": "Call initiated!", "call_sid": call.sid}

# ✅ Handle WebSockets for Deepgram STT
@app.websocket("/stt-stream")
async def stt_websocket(websocket: WebSocket):
    await websocket.accept()
    deepgram_client = deepgram.Deepgram(os.getenv("DEEPGRAM_API_KEY"))

    async for message in websocket.iter_text():
        transcript = deepgram_client.transcribe(message)  # Simulated transcription
        response = get_grok_response(transcript)
        await websocket.send_text(response)

# ✅ Call Grok API
def get_grok_response(text):
    grok_api_key = os.getenv("GROK_API_KEY")
    response = openai.ChatCompletion.create(
        model="grok-1",
        messages=[{"role": "system", "content": text}],
        api_key=grok_api_key
    )
    return response["choices"][0]["message"]["content"]

# ✅ Convert LLM Response to Speech using Azure TTS
def text_to_speech(text):
    from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
    speech_config = SpeechConfig(subscription=os.getenv("AZURE_TTS_KEY"), region="eastus")
    synthesizer = SpeechSynthesizer(speech_config=speech_config)
    synthesizer.speak_text_async(text)



# print(f"SID: {TWILIO_ACCOUNT_SID}")
# print(f"Token: {TWILIO_AUTH_TOKEN}")

# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# try:
#     account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
#     print("✅ Twilio credentials are valid!")
# except Exception as e:
#     print(f"❌ Authentication Failed: {e}")
    
# import os
# print(f"Twilio Number: {os.getenv('TWILIO_PHONE_NUMBER')}")
