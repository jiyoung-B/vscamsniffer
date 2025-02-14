import json
import speech_recognition as sr
from channels.generic.websocket import AsyncWebsocketConsumer
import os
from dotenv import load_dotenv
import requests 
from elevenlabs import ElevenLabs
from elevenlabs import play
import asyncio

load_dotenv()

ele_api_key = os.environ.get("API_KEY")
voice_id = "PLfpgtLkFW07fDYbUiRJ"  # 등록된 목소리 ID
model_id = "eleven_multilingual_v2"
output_path = "media/audio/response.mp3" 
print(f"APIKEY:{ele_api_key}")


client = ElevenLabs(
    api_key=ele_api_key,
)
# audio = client.text_to_speech.convert(
#     voice_id="PLfpgtLkFW07fDYbUiRJ",
#     output_format="mp3_44100_128",
#     text=bot_response,
#     model_id="eleven_multilingual_v2",
# )




class RPConsumer(AsyncWebsocketConsumer):
    #웹소켓 연결
    async def connection(self):
        await self.accept()
        await self.send(text_data=json.dump({"message": "Websocket 연결완료"}))

    async def disconnectin(self):
        print("연결 안됨")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        bot_response = f"당신이 '{message}'라고 말했군요!"
        # 클라이언트에게 응답 전송
        await self.send(text_data=json.dumps({"message": bot_response}))

        if bot_response:
            async def tts_task():
                client = ElevenLabs(
                api_key=ele_api_key,
                )
                audio = client.text_to_speech.convert(
                voice_id="PLfpgtLkFW07fDYbUiRJ",
                output_format="mp3_44100_128",
                text=bot_response,
                model_id="eleven_multilingual_v2",
                )
                play(audio)
                # await self.send(text_data=json.dumps({"status": "TTS 변환 완료"}))

            asyncio.create_task(tts_task())



