import asyncio
import json
import torch
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from transformers import AutoTokenizer
from rp.model_loader import load_model_and_tokenizer  # 모델 로드 함수 import

class SolutionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("웹소켓 연결 완료")

        # 모델과 토크나이저 로드
        self.model, self.tokenizer = load_model_and_tokenizer()
        self.current_scenario = None  

        self.scenarios = {
            "통장에서 돈이 인출": "통장에서 돈이 인출되었어요.",
            "개인정보를 유출했어요.": "개인정보 유출이 되었어요."
        }

        self.conversation_history = []

        # 종료 토큰 설정
        self.terminators = [self.tokenizer.convert_tokens_to_ids("<|eot_id|>")]

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

                initial_message = f"{scenario_name} 경우에 대한 해결방안입니다."
                user_message = initial_message
                await self.send(text_data=json.dumps({"message": initial_message}))

                if user_message:
                    self.conversation_history.append({"role": "user", "content": user_message})

                    # 입력 생성 (비동기 처리 제거)
                    input_ids = self.tokenizer.apply_chat_template(
                        self.conversation_history,
                        add_generation_prompt=True,
                        return_tensors="pt"
                    ).to(self.model.device)

                    # 생성 설정
                    with torch.inference_mode():
                        if torch.cuda.is_available():
                            with torch.cuda.amp.autocast():
                                outputs = self.model.generate(
                                    input_ids,
                                    max_length=256,
                                    eos_token_id=self.tokenizer.eos_token_id,
                                    pad_token_id=self.tokenizer.eos_token_id,
                                    do_sample=False,
                                    use_cache=True
                                )
                        else:
                            outputs = self.model.generate(
                                input_ids,
                                max_length=256,
                                eos_token_id=self.tokenizer.eos_token_id,
                                pad_token_id=self.tokenizer.eos_token_id,
                                do_sample=False,
                                use_cache=True
                            )

                    # 응답 디코딩
                    generated_text = self.tokenizer.decode(
                        outputs[0][input_ids.shape[-1]:],
                        skip_special_tokens=True
                    )

                    # 응답 전송
                    await self.send(text_data=json.dumps({
                        "message": generated_text
                    }))

        except Exception as e:
            print(f"메시지 처리 중 오류 발생: {e}")
            traceback.print_exc()
            await self.send(text_data=json.dumps({
                "message": "죄송합니다. 메시지 처리 중 오류가 발생했습니다."
            }))

    async def disconnect(self, close_code):
        torch.cuda.empty_cache()
