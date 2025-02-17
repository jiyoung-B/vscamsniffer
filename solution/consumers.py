from channels.generic.websocket import AsyncWebsocketConsumer
import json



class SolutionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_solution_options()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        selected_option = text_data_json["option"]
        
        await self.send(text_data=json.dumps({
                "message": selected_option,
                "options": self.get_next_options(selected_option)
            }))
        
    async def send_solution_options(self):
        #첫번째 질문
        options = [
            "통장에서 돈이 인출되었어요.",
            "개인정보 및 신용정보를 누출했어요."
        ]
        await self.send(text_data=json.dumps({
            "options": options
        }))

    def get_next_options(self, previous_option):
        #두번째 질문
        options_map = {
            "더 궁금하신 사항이 있으신가요?": [
                "네",
                "아니요. 없습니다"
            ],
            # 필요시 추가예정
        }
        return options_map.get(previous_option, [])

