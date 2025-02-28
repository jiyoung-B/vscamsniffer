import json
import base64
import torch
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from transformers import AutoTokenizer
from rp.model_loader import load_model_and_tokenizer
from rp.rag_load import initialize_rag, get_scenario_content, get_strategy_content
from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.settings import Settings
import gc

load_dotenv()

# Initialize ElevenLabs client
ele_api_key = os.environ.get("API_KEY")
if not ele_api_key:
    print("Warning: ElevenLabs API key not found in environment variables")
    
voice_id = "PLfpgtLkFW07fDYbUiRJ"
model_id = "eleven_multilingual_v2"
client = ElevenLabs(api_key=ele_api_key)

# Disable OpenAI API
Settings.llm = None

class RPConsumer(AsyncWebsocketConsumer):
    model = None
    tokenizer = None
    PROMPT = None  
    PROMPT2 = None  
    scenario_index = None
    strategy_index = None
    
    @classmethod
    async def initialize_if_needed(cls):
        if cls.model is None or cls.tokenizer is None:
            cls.model, cls.tokenizer = await asyncio.to_thread(load_model_and_tokenizer)
        
        if cls.scenario_index is None or cls.strategy_index is None:
            cls.scenario_index, cls.strategy_index = await initialize_rag()

    # 웹사이트 실행시 웹소캣연결+rag+프롬프트 설정+히스토리 초기화
    async def connect(self):
        # 웹소켓 타임아웃 설정(초)
        self.close_timeout = 120
        await self.accept()
        print("웹소켓 연결 완료")

        try:    
            # 모델 초기화
            await self.initialize_if_needed()
            
            # 시스템 프롬프트 설정
            self.PROMPT = '''당신은 보이스피싱 범죄자를 연기하는 AI입니다. 사용자가 보이스피싱 상황을 직접 경험하고, 올바른 대응법을 학습할 수 있도록 돕는 것이 목표입니다.

            **규칙:**
            1. 응답은 반드시 **한국어**로 작성하세요.
            2. 사용자의 입력에 대해 **실제 보이스피싱 범죄자처럼 현실감 있는 대사**를 작성하세요.
            3. **역할명 없이 응답만 출력**하며, 자연스럽게 범죄자 역할을 수행하세요.
            4. **설득력 있는 어조**를 유지하고, 상황에 맞게 구체적인 보이스피싱 수법을 사용하세요.
            5. 문장은 **1~2문장으로 간결하게 작성**하세요.
            6. 사용자가 **"대화 종료"**라고 입력하면 대화를 즉시 종료하세요.

            **예시 시나리오:**
            - **경찰 사칭:** "고객님의 계좌에서 불법 거래가 감지되었습니다. 본인 확인을 위해 지금 즉시 주민등록번호와 계좌번호를 알려주세요."
            - **은행 사칭:** "대출 승인이 완료되었으니, 신속한 처리를 위해 계좌 정보를 입력해주시기 바랍니다."
            - **가족 납치:** "당신의 가족이 납치되었습니다. 안전하게 돌려받으려면 지금 당장 송금하세요."

            **보이스피싱 시나리오 추가 참고 정보**
            {method_scenario}

            **목표:**  
            사용자가 실제 보이스피싱 상황처럼 몰입하여 대응법을 학습할 수 있도록, **자연스럽고 설득력 있는 보이스피싱 범죄자의 역할을 수행하세요.**'''


            self.PROMPT2 = '''
            당신은 사용자의 보이스피싱 대응을 평가하는 AI입니다. 사용자가 보이스피싱 상황을 경험하고 **올바른 대응법을 학습할 수 있도록** 돕는 것이 목표입니다.
            
            **평가 예시:**  
            - **부적절한 대응:** *"제가 계좌번호를 알려주면 되나요?"*  
              → *"보이스피싱 범죄자는 계좌번호와 같은 개인 정보를 요구합니다. 절대 제공하면 안 됩니다. 이런 상황에서는 경찰이나 금융기관의 공식 번호로 직접 문의하세요."*  
            - **적절한 대응:** *"전화를 끊고 직접 은행에 확인해보겠습니다."*  
              → *"올바른 대응입니다! 보이스피싱 전화를 받았다면 즉시 전화를 끊고, 공식적인 기관을 통해 사실을 확인하는 것이 중요합니다."*
        
            **보이스피싱 올바른 대응방법 추가 참고 정보**
            {method_strategy}

            **목표:**  
            사용자가 보이스피싱 상황에서 **올바르게 대응할 수 있도록 구체적인 피드백을 제공하고, 더 나은 대응법을 학습할 수 있도록 돕습니다.**'''


            self.conversation_history = []
            self.terminators = [
                self.tokenizer.eos_token_id,
                self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]
            
        except Exception as e:
            print(f"초기화 중 오류 발생: {e}")
            await self.close()

    #연결이 끊길 경우        
    async def disconnect(self, close_code):
        print(f"WebSocket 연결 종료 (close_code: {close_code})")
        
        # 메모리 정리
        try:
            torch.cuda.empty_cache()
            gc.collect()
        except Exception as e:
            print(f"메모리 정리 중 오류: {e}")
        
        # close_code가 특정 값일 경우 추가 로그 출력
        if close_code is not None:
            print(f"WebSocket 종료 코드: {close_code}")

        # 필요하다면 로그 파일에 저장
        with open("websocket_errors.log", "a") as log_file:
            log_file.write(f"WebSocket 종료 - 코드: {close_code}\n")

        # 기본 WebSocket 종료 처리
        await super().disconnect(close_code)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get("type", "message")
            user_message = text_data_json.get("message", "").strip()

            if message_type == "scenario_select":
                scenario_name = text_data_json.get("scenario")
                if not scenario_name:
                    raise ValueError("시나리오가 선택되지 않았습니다")

                self.current_scenario = scenario_name
                
                # RAG 데이터 가져오기
                method_scenario = get_scenario_content(self.scenario_index)
                
                # 시스템 프롬프트에 RAG 데이터 삽입
                formatted_prompt = self.PROMPT.format(method_scenario=method_scenario)
                
                self.conversation_history = [{
                    "role": "system",
                    "content": formatted_prompt
                }]
                
                # 시나리오 선택 후, 유저가 입력한 것처럼 대화 기록에 추가
                self.conversation_history.append({"role": "user", "content": scenario_name})

                # 시나리오 정의 및 대화 컨텍스트 준비
                scenario_prompt = f"Scenario: {self.current_scenario}\n"
                conversation_with_scenario = self.conversation_history.copy()
                conversation_with_scenario.append({"role": "system", "content": scenario_prompt})

                input_ids = self.tokenizer.apply_chat_template(
                    conversation_with_scenario,
                    add_generation_prompt=True,
                    return_tensors="pt"
                ).to(self.model.device)

                attention_mask = (input_ids != self.tokenizer.pad_token_id).long()

                # 응답 생성, 추후 오디오 데이터 넣을 예정
                output = await self.generate_response(input_ids, attention_mask)
                audio_data = await self.generate_tts(output)
                
                self.conversation_history.append({"role": "assistant", "content": output})

                await self.send(text_data=json.dumps({
                    "message": output,
                    "audio":audio_data
                }))
                return

            print(f"usermessage:{user_message}")

            if user_message in ["대화 종료", "대화종료"]:
                await self.feedbacktext(user_message)
                return
            
            if not user_message:
                await self.send(text_data=json.dumps({
                    "message": "대화문으로 글자를 입력해주세요."
                }))
                return
            
            self.conversation_history.append({"role": "user", "content": user_message})
            
            input_ids = self.tokenizer.apply_chat_template(
                self.conversation_history,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(self.model.device)

            attention_mask = (input_ids != self.tokenizer.pad_token_id).long()
            
            # 응답 생성, 추후 음성 데이터 삽입예정
            output = await self.generate_response(input_ids, attention_mask)
            audio_data = await self.generate_tts(output)
            
            self.conversation_history.append({"role": "assistant", "content": output})

            await self.send(text_data=json.dumps({
                "message": output,
                "audio":audio_data
            }))
            
        except Exception as e:
            print(f"메시지 처리 중 상세 오류: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"메시지 처리 중 오류가 발생했습니다: {str(e)}"
            }))

    # 응답 생성 로직을 별도 메소드로 분리
    async def generate_response(self, input_ids, attention_mask):
        try:
            # GPU 메모리 사용
            with torch.inference_mode(), torch.cuda.amp.autocast():
                outputs = self.model.generate(
                    input_ids,
                    attention_mask=attention_mask,
                    max_new_tokens=128,
                    eos_token_id=self.terminators,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    return_dict_in_generate=True,
                    output_scores=True
                )
        # GPU 소진시 CPU 전환
        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
                print("GPU 메모리 부족으로 CPU로 전환합니다!")
                device = torch.device("cpu")
                self.model.to(device)
                input_ids = input_ids.to(device)
                attention_mask = attention_mask.to(device)

                with torch.inference_mode():
                    outputs = self.model.generate(
                        input_ids,
                        attention_mask=attention_mask,
                        max_new_tokens=128,
                        eos_token_id=self.terminators,
                        do_sample=True,
                        temperature=0.6,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
            else:
                raise e

        # 안전한 출력 처리
        if not isinstance(outputs, torch.Tensor) and hasattr(outputs, 'sequences'):
            generated_sequence = outputs.sequences[0]
        else:
            generated_sequence = outputs[0]

        # 입력 길이 이후의 토큰만 디코딩
        input_length = input_ids.shape[-1]
        if len(generated_sequence) > input_length:
            new_tokens = generated_sequence[input_length:]
            generated_text = self.tokenizer.decode(
                new_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
        else:
            generated_text = "응답을 생성하지 못했습니다."

        print("Assistant:", generated_text, "\n")
        return generated_text



    async def feedbacktext(self, user_message,close_code=1000):
        try:
            if user_message in ["대화 종료", "대화종료", "exit", "quit"]:
                await self.send(text_data=json.dumps({
                    "type": "feedback start",
                    "message": "롤플레잉 피드백을 작성중입니다. 잠시만 기다려주세요.",
                }))

            # RAG 전략 데이터 가져오기
            method_strategy = get_strategy_content(self.strategy_index)
            
            # 프롬프트에 RAG 데이터 삽입
            formatted_prompt = self.PROMPT2.format(method_strategy=method_strategy)

            conversation_history_eval = [
                {"role": "system", "content": formatted_prompt}
            ]
            
            # 롤플레잉 대화 내역을 평가용 이력에 추가 (첫 시스템 메시지 제외)
            for i in range(1, len(self.conversation_history)):
                conversation_history_eval.append(self.conversation_history[i])
            
            # 모델에 평가 요청
            input_ids_eval = self.tokenizer.apply_chat_template(
                conversation_history_eval,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(self.model.device)
            
            attention_mask_eval = (input_ids_eval != self.tokenizer.pad_token_id).long()
            
            # GPU 사용
            try:
                with torch.inference_mode(), torch.cuda.amp.autocast():
                    eval_outputs = self.model.generate(
                        input_ids_eval,
                        attention_mask=attention_mask_eval,
                        max_new_tokens=256,  # 피드백은 더 길게
                        eos_token_id=self.terminators,
                        do_sample=True,
                        temperature=0.6,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
            # GPU 소진시 CPU 전환
            except RuntimeError as e:
                if "CUDA out of memory" in str(e):
                    print("GPU 메모리 부족으로 CPU로 전환합니다!")
                    device = torch.device("cpu")
                    self.model.to(device)
                    input_ids_eval = input_ids_eval.to(device)
                    attention_mask_eval = attention_mask_eval.to(device)

                    with torch.inference_mode():
                        eval_outputs = self.model.generate(
                            input_ids_eval,
                            attention_mask=attention_mask_eval,
                            max_new_tokens=256,
                            eos_token_id=self.terminators,
                            do_sample=True,
                            temperature=0.6,
                            top_p=0.9,
                            pad_token_id=self.tokenizer.pad_token_id
                        )
                else:
                    raise e

            # 입력 길이 이후의 토큰만 디코딩
            input_length = input_ids_eval.shape[-1]
            if len(eval_outputs[0]) > input_length:
                new_tokens = eval_outputs[0][input_length:]
                feedback_text = self.tokenizer.decode(
                    new_tokens,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True
                )
            else:
                feedback_text = "피드백을 생성하지 못했습니다."
            
            print("Feedback:", feedback_text, "\n")
            
            # 피드백 전송
            await self.send(text_data=json.dumps({
                "type": "feedback",
                "message": feedback_text
            }))
            
            # 대화 완전 종료 알림
            await self.send(text_data=json.dumps({
                "type": "conversation_end",
                "message": "대화가 종료되었습니다."
            }))
            await self.close(code=close_code)
            
        except Exception as e:
            print(f"피드백 생성 중 오류: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"피드백 생성 중 오류가 발생했습니다: {str(e)}"
            }))

    # tts생성
    async def generate_tts(self, text):
        try:
            if not ele_api_key:
                print("ElevenLabs API key is missing")
                return None
                
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=text,
                model_id=model_id,
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
