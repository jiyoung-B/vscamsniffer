from django.apps import AppConfig
from rp.rag_load import initialize_rag
import asyncio
import torch

def ready_model():
    model, tokenizer = load_model_and_tokenizer()

class RpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rp'

    def ready(self):
        from rp.model_loader import load_model_and_tokenizer
        import asyncio
        import torch

        #서버실행시 모델,토크나이저,rag 대기시키기
        torch.cuda.empty_cache()
        # 모델 초기화
        self.model, self.tokenizer = load_model_and_tokenizer()
    
        
        # RAG 초기화
        asyncio.run(self.initialize_rag_async())

        print("모델, 토크나이저, RAG가 서버 시작 시 초기화되었습니다.")


    async def initialize_rag_async(self):
        await initialize_rag()

