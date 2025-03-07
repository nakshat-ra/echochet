# from fastapi import FastAPI, WebSocket, Response
# import os
# import openai
# import deepgram
# from twilio.twiml.voice_response import VoiceResponse
# from twilio.rest import Client
# import uvicorn
# from fastapi import Form

# from dotenv import load_dotenv
# load_dotenv(dotenv_path=".env")


# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "Voice AI Agent Running"}


# # ✅ Handle Incoming Twilio Calls
# @app.post("/incoming-call")
# async def handle_call():
#     response = VoiceResponse()
#     response.say("Connecting you to the AI assistant. Please speak after the beep.")
#     response.pause(length=1)
#     response.record(timeout=10, transcribe=True)  # Records user input
#     # return str(response)
#     return Response(content=str(response), media_type="application/xml")

# # ✅ Initiate Outbound Call using Twilio
# #added form after str
# @app.post("/make-call")
# async def make_call(to_phone_number: str = Form(...)):
#     TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
#     TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
#     TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

#     client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

#     call = client.calls.create(
#         to=to_phone_number,
#         from_=TWILIO_PHONE_NUMBER,
#         url="https://echochet-azaqfbfhfvcgf5g2.eastus2-01.azurewebsites.net/incoming-call"  # Change to your deployed Azure webhook
#     )

#     return {"message": "Call initiated!", "call_sid": call.sid}

# # ✅ Handle WebSockets for Deepgram STT
# @app.websocket("/stt-stream")
# async def stt_websocket(websocket: WebSocket):
#     await websocket.accept()
#     deepgram_client = deepgram.Deepgram(os.getenv("DEEPGRAM_API_KEY"))

#     async for message in websocket.iter_text():
#         transcript = deepgram_client.transcribe(message)  # Simulated transcription
#         response = get_grok_response(transcript)
#         await websocket.send_text(response)

# # ✅ Call Grok API
# def get_grok_response(text):
#     grok_api_key = os.getenv("GROK_API_KEY")
#     response = openai.ChatCompletion.create(
#         model="grok-1",
#         messages=[{"role": "system", "content": text}],
#         api_key=grok_api_key
#     )
#     return response["choices"][0]["message"]["content"]

# # ✅ Convert LLM Response to Speech using Azure TTS
# def text_to_speech(text):
#     from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
#     speech_config = SpeechConfig(subscription=os.getenv("AZURE_TTS_KEY"), region="eastus")
#     synthesizer = SpeechSynthesizer(speech_config=speech_config)
#     synthesizer.speak_text_async(text)



# # print(f"SID: {TWILIO_ACCOUNT_SID}")
# # print(f"Token: {TWILIO_AUTH_TOKEN}")

# # client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# # try:
# #     account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
# #     print("✅ Twilio credentials are valid!")
# # except Exception as e:
# #     print(f"❌ Authentication Failed: {e}")
    
# # import os
# # print(f"Twilio Number: {os.getenv('TWILIO_PHONE_NUMBER')}")






from fastapi import FastAPI, WebSocket, Response, Form
import os
import openai
import deepgram
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import uvicorn
from dotenv import load_dotenv
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer

# Load environment variables
load_dotenv(dotenv_path=".env")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Voice AI Agent Running"}

# ✅ Handle Incoming Twilio Calls and AI Conversation
@app.post("/incoming-call")
async def handle_call():
    response = VoiceResponse()
    response.say("Connecting you to the AI assistant. Please speak after the beep.")
    response.pause(length=1)
    response.record(timeout=10, transcribe=True)
    return Response(content=str(response), media_type="application/xml")

# ✅ Initiate Outbound Call using Twilio
#changed just str to str = Form for local testing
#changed Form to Body for API/azure based testing
@app.post("/make-call")
async def make_call(to_phone_number: str = Body(...)):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=to_phone_number,
        from_=TWILIO_PHONE_NUMBER,
        url="https://echochet-azaqfbfhfvcgf5g2.eastus2-01.azurewebsites.net/incoming-call"
    )
    return {"message": "Call initiated!", "call_sid": call.sid}

# ✅ Handle WebSockets for Deepgram STT
@app.websocket("/stt-stream")
async def stt_websocket(websocket: WebSocket):
    await websocket.accept()
    deepgram_client = deepgram.Deepgram(DEEPGRAM_API_KEY)
    
    async for message in websocket.iter_text():
        transcript = deepgram_client.transcribe(message)  # Speech-to-text
        response = get_llm_response(transcript)  # Get AI response
        speech_output = text_to_speech(response)  # Convert AI response to speech
        await websocket.send_text(speech_output)

# ✅ Get Response from LLM (Grok/OpenAI)
def get_llm_response(text):
    response = openai.ChatCompletion.create(
        model="grok-1",
        messages=[{"role": "system", "content": text}],
        api_key=os.getenv("OPENAI_API_KEY")
    )
    return response["choices"][0]["message"]["content"]

# ✅ Convert AI Response to Speech using Azure TTS
def text_to_speech(text):
    speech_config = SpeechConfig(subscription=AZURE_TTS_KEY, region="eastus2")
    synthesizer = SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(text).get()
    return result
