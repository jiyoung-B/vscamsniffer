import asyncio
import json
import torch
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from transformers import AutoTokenizer
from rp.model_loader import load_model_and_tokenizer  # 모델 로드 함수 import
from rp.rag_load import initialize_rag, get_strategy_content

class SolutionConsumer(AsyncWebsocketConsumer):
    model = None
    tokenizer = None
    PROMPT3 = None
    PROMPT4 = None
    strategy_index = None

    @classmethod
    async def initialize_if_needed(cls):
        if cls.model is None or cls.tokenizer is None:
            cls.model, cls.tokenizer = await asyncio.to_thread(load_model_and_tokenizer)
        
        if cls.strategy_index is None:
            cls.strategy_index = await initialize_rag()


    async def connect(self):
        self.close_timeout = 120

        await self.accept()
        print("웹소켓 연결 완료")


        # 모델과 토크나이저 로드
        # self.model, self.tokenizer = load_model_and_tokenizer()
        await self.initialize_if_needed()
        self.current_scenario = None 

        method_strategy = get_strategy_content(self.strategy_index)

        self.PROMPT3 = f'''네 역할은 보이스피싱에 대한 대응방법을 알려주는거야. 
        
        **규칙**
        1. 반드시 한국어로 작성해야해.
        2. 다른 언어가 포함되어 있다면 제외해줘.
        3. 맞춤법 맞춰서 작성해줘. 
        
        **보이스피싱 올바른 대응방법 추가 참고 정보**
        {method_strategy}
        '''

        PROMPT4 = f'''네 역할은 보이스피싱에 대한 대응방법을 알려주는거야.
        
        **규칙**
        1. 반드시 한국어로 작성해야해.
        2. 다른 언어가 포함되어 있다면 제외해줘.
        3. 맞춤법 맞춰서 작성해줘.
        
        **보이스피싱 올바른 대응방법 추가 참고 정보**
        {method_strategy}
        '''

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

                # 프롬프트 삽입
                if scenario_name == "보이스피싱 인출":
                    prompt = self.PROMPT3
                elif scenario_name == "보이스피싱 개인정보 유출":
                    prompt = self.PROMPT4
                else:
                    prompt = "사용자가 보이스피싱 피해 상황을 경험했습니다. 이 상황에 대한 적절한 대처방안을 3~4가지 제안해주세요."


                self.conversation_history = [{
                    "role": "system",
                    "content": prompt
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
