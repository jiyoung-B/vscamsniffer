import json
import speech_recognition as sr
from channels.generic.websocket import AsyncWebsocketConsumer


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