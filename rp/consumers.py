import json
import speech_recognition as sr
from channels.generic.websocket import AsyncWebsocketConsumer
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
import base64
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import asyncio
from functools import lru_cache

load_dotenv()

# Environment variables
ele_api_key = os.environ.get("API_KEY")
voice_id = "PLfpgtLkFW07fDYbUiRJ"
model_id = "eleven_multilingual_v2"

# Initialize ElevenLabs client
client = ElevenLabs(api_key=ele_api_key)

# 모델 불러오기
from rp.model_loader import load_model_and_tokenizer

model, tokenizer = load_model_and_tokenizer()

class RPConsumer(AsyncWebsocketConsumer):
    model = None
    tokenizer = None
    
    @classmethod
    async def initialize_if_needed(cls):
        if cls.model is None or cls.tokenizer is None:
            cls.model, cls.tokenizer = await asyncio.to_thread(load_model_and_tokenizer)
    
    async def connect(self):
        await self.accept()
        print("웹소켓 연결 완료")
        
        # 비동기적으로 모델 초기화
        await self.initialize_if_needed()
        
        # 시나리오별 시스템 프롬프트 설정
        self.scenarios = {
            "경찰 사칭": "당신은 경찰을 사칭하는 보이스피싱 사기범입니다. 사용자의 개인정보와 금전을 탈취하려 합니다.",
            "은행 사칭": "당신은 은행원을 사칭하는 보이스피싱 사기범입니다. 계좌 정보와 금전을 탈취하려 합니다.",
            "대출 사칭": "당신은 대출 상담사를 사칭하는 보이스피싱 사기범입니다. 대출을 미끼로 금전을 탈취하려 합니다.",
            "가족 납치": "당신은 가족을 납치했다고 협박하는 보이스피싱 사기범입니다. 협박으로 금전을 탈취하려 합니다.",
            "협박": "당신은 개인정보 해킹을 빙자한 보이스피싱 사기범입니다. 협박으로 금전을 탈취하려 합니다."
        }
        
        self.current_scenario = None
        self.conversation_history = []
        
        self.terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        if text_data_json.get("type") == "scenario_select":
            # 시나리오 선택 처리
            scenario_name = text_data_json["scenario"]
            self.current_scenario = scenario_name
            
            # 시나리오에 맞는 시스템 프롬프트 설정
            self.conversation_history = [{
                "role": "system",
                "content": self.scenarios.get(scenario_name, "기본 보이스피싱 시나리오입니다.")
            }]
            
            # 시나리오 시작 메시지 전송
            initial_message = f"{scenario_name} 시나리오를 시작합니다."
            await self.send(text_data=json.dumps({"message": initial_message}))
            return
        
        # 일반 메시지 처리
        user_message = text_data_json.get("message")
        if not user_message:
            return
            
        self.conversation_history.append({"role": "user", "content": user_message})
        
        try:
            # 입력 생성
            input_ids = await asyncio.to_thread(
                self.tokenizer.apply_chat_template,
                self.conversation_history,
                add_generation_prompt=True,
                return_tensors="pt"
            )
            input_ids = input_ids.to(self.model.device)
            
            # 메모리 효율적인 생성 설정
            with torch.inference_mode(), torch.cuda.amp.autocast():
                outputs = await asyncio.to_thread(
                    self.model.generate,
                    input_ids,
                    max_new_tokens=256,
                    eos_token_id=self.terminators,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=True,
                )
            
            # 응답 디코딩
            generated_text = await asyncio.to_thread(
                self.tokenizer.decode,
                outputs[0][input_ids.shape[-1]:],
                skip_special_tokens=True
            )
            
            # TTS 생성
            audio_data = await self.generate_tts(generated_text)
            
            # 응답 전송
            await self.send(text_data=json.dumps({
                "message": generated_text,
                "audio": audio_data
            }))
            
            # 대화 기록 업데이트 및 제한
            self.conversation_history.append({"role": "assistant", "content": generated_text})
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
                
        except Exception as e:
            print(f"메시지 처리 중 오류 발생: {e}")
            await self.send(text_data=json.dumps({
                "message": "죄송합니다. 메시지 처리 중 오류가 발생했습니다."
            }))

    async def generate_tts(self, text):
        try:
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=text,
                model_id=model_id,
            )
            
            audio_bytes = b''.join(list(audio_stream))
            if audio_bytes:
                return base64.b64encode(audio_bytes).decode('utf-8')
            return None
        except Exception as e:
            print(f"TTS 변환 중 오류 발생: {e}")
            return None

    async def disconnect(self, close_code):
        torch.cuda.empty_cache()
