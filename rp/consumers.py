import json
import speech_recognition as sr
from channels.generic.websocket import AsyncWebsocketConsumer
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from elevenlabs import play
from io import BytesIO
import base64
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.settings import Settings
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer
from safetensors.torch import load_file


load_dotenv()

ele_api_key = os.environ.get("API_KEY")
voice_id = "PLfpgtLkFW07fDYbUiRJ"  # 등록된 목소리 ID
model_id = "eleven_multilingual_v2"
output_path = "media/audio/response.mp3" 
print(f"APIKEY:{ele_api_key}")


client = ElevenLabs(
    api_key=ele_api_key,
)


class RPConsumer(AsyncWebsocketConsumer):
    # 웹소켓 연결
    async def connect(self):
        await self.accept()
        print("웹소켓 연결 완료")
        
    async def send_rp_options(self):
        #첫번째 질문
        options = [
            "경찰 사칭",
            "은행 사칭",
            "대출 사칭"
        ]
        await self.send(text_data=json.dumps({
            "options": options
        }))


    # 클라이언트 메시지 수신
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        bot_response = f"당신이 '{message}'라고 말했군요!"

        # TTS 변환을 비동기로 실행하고 audio 데이터 얻기
        audio_data = await self.generate_tts(bot_response)
        
        # 응답 데이터 준비
        response_data = {
            "message": bot_response,
            "audio": audio_data
        }

        # 클라이언트에게 텍스트와 오디오 데이터 함께 전송
        await self.send(text_data=json.dumps(response_data))

    # TTS 생성
    async def generate_tts(self, text):
        try:
            client = ElevenLabs(api_key=ele_api_key)
            audio_stream = client.text_to_speech.convert(
                voice_id="PLfpgtLkFW07fDYbUiRJ",
                output_format="mp3_44100_128",
                text=text,
                model_id="eleven_multilingual_v2",
            )
            
            # Convert generator to bytes
            audio_bytes = b''
            for chunk in audio_stream:
                audio_bytes += chunk
            
            if audio_bytes:
                # Convert to base64
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                return audio_base64
            else:
                print("오디오 변환 실패")
                return None

        except Exception as e:
            print(f"TTS 변환 중 오류 발생: {e}")
            return None





