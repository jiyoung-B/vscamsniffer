# from channels.generic.websocket import AsyncWebsocketConsumer
# import json



# class SolutionConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.send_solution_options()

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         selected_option = text_data_json["option"]
        
#         await self.send(text_data=json.dumps({
#                 "message": selected_option,
#                 "options": self.get_next_options(selected_option)
#             }))
        
#     async def send_solution_options(self):
#         #첫번째 질문
#         options = [
#             "통장에서 돈이 인출되었어요.",
#             "개인정보 및 신용정보를 누출했어요."
#         ]
#         await self.send(text_data=json.dumps({
#             "options": options
#         }))

#     def get_next_options(self, previous_option):
#         #두번째 질문
#         options_map = {
#             "더 궁금하신 사항이 있으신가요?": [
#                 "네",
#                 "아니요. 없습니다"
#             ],
#             # 필요시 추가예정
#         }
#         return options_map.get(previous_option, [])
import json
import speech_recognition as sr
from channels.generic.websocket import AsyncWebsocketConsumer
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
import torch
import asyncio
from transformers import AutoTokenizer
from functools import lru_cache
import torch



loaded_model = None

@lru_cache(maxsize=1)
def load_model_and_tokenizer():
    global loaded_model
    
    # 모델이 이미 로드된 경우 캐시된 모델을 반환
    if loaded_model is not None:
        print("모델이 이미 로드되어 있습니다.")
        return loaded_model

class SolutionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("웹소켓 연결 완료")
        
        # 모델과 토크나이저 로드
        self.model = model
        self.tokenizer = tokenizer
        
        self.scenarios = {
            "통장에서 돈이 인출": "통장에서 돈이 인출되었어요.",
            "개인정보를 유출했어요.": "개인정보 유출이 되었어요."
        }

        self.current_scenario = None
        self.conversation_history = []

        self.terminators = [
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)

            if text_data_json.get("type") == "scenario_select":
                # 시나리오 선택 처리
                scenario_name = text_data_json["scenario"]
                self.current_scenario = scenario_name

                self.conversation_history = [{
                    "role": "system",
                    "content": self.scenarios.get(scenario_name, 
                        "사용자가 보이스피싱 피해 상황을 경험했습니다. 이 상황에 대한 적절한 대처방안을 3~4가지 제안해주세요.")
                }]

                initial_message = f"{scenario_name} 시나리오를 시작합니다."
                await self.send(text_data=json.dumps({"message": initial_message}))
                return

            # 사용자 입력 처리
            user_message = text_data_json.get("message")
            if user_message:
                self.conversation_history.append({"role": "user", "content": user_message})
                # 모델과 토크나이저를 로드하는 예시

                tokenizer = AutoTokenizer.from_pretrained('모델_이름')

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
                        max_length=256,  # 생성할 최대 길이
                        eos_token_id=tokenizer.eos_token_id,  # 종료 토큰을 설정하여, 생성 후 종료
                        do_sample=False,  # 샘플링을 비활성화하여 모델이 한번만 응답하고 종료하도록 설정
                        pad_token_id=tokenizer.eos_token_id,  # 패딩 토큰을 eos_token으로 설정
                        use_cache=True,  # 캐시를 사용할 경우
                                        )


                
                # 응답 디코딩
                generated_text = await asyncio.to_thread(
                    self.tokenizer.decode,
                    outputs[0][input_ids.shape[-1]:],
                    skip_special_tokens=True
                )

                # 응답 전송
                await self.send(text_data=json.dumps({
                    "message": generated_text
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

    async def disconnect(self, close_code):
        torch.cuda.empty_cache()





    # async def receive(self, text_data):
    #     """웹소켓으로부터 입력을 받아 LLM으로 응답 생성"""
    #     user_input = text_data.strip()

    #     # LLM을 활용하여 답변 생성
    #     response_text = await self.generate_response(user_input)

    #     # 클라이언트로 결과 전송
    #     await self.send(text_data=response_text)
    
    # async def generate_response(self, user_input):
    #     """LLM을 이용해 대처방안 생성"""
    #     prompt = f"사용자가 '{user_input}' 상황을 경험했습니다. 이 상황에 대한 적절한 대처방안을 3~4가지 제안해주세요."

    #     # LLM 모델 실행 (예시: transformers 사용)
    #     inputs = self.tokenizer(prompt, return_tensors="pt")
    #     output = self.model.generate(**inputs, max_length=500)
    #     response_text = self.tokenizer.decode(output[0], skip_special_tokens=True)

    #     return response_text

