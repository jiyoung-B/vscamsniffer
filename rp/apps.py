from django.apps import AppConfig
from rp.rag_load import initialize_rag
import asyncio
import torch

class RpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rp'
    
    # 모델과 토크나이저를 클래스 변수로 선언 (None으로 초기화)
    model = None
    tokenizer = None

    def ready(self):
        # 이미 모델이 로드되어 있으면 다시 로드하지 않음
        if RpConfig.model is not None and RpConfig.tokenizer is not None:
            print("모델과 토크나이저가 이미 로드되어 있습니다.")
            return
        
        from rp.model_loader import load_model_and_tokenizer
        
        print("모델과 토크나이저 로드 시작...")
        torch.cuda.empty_cache()
        # 모델 초기화 (클래스 변수에 저장)
        RpConfig.model, RpConfig.tokenizer = load_model_and_tokenizer()
        
        # RAG 초기화
        asyncio.run(self.initialize_rag_async())
        
        print("모델, 토크나이저, RAG가 서버 시작 시 초기화되었습니다.")

    async def initialize_rag_async(self):
        await initialize_rag()

# from django.apps import AppConfig
# from rp.rag_load import initialize_rag
# import asyncio
# import torch

# def ready_model():
#     model, tokenizer = load_model_and_tokenizer()

# class RpConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'rp'

#     def ready(self):
#         from rp.model_loader import load_model_and_tokenizer
#         import asyncio
#         import torch

#         #서버실행시 모델,토크나이저,rag 대기시키기
#         torch.cuda.empty_cache()
#         # 모델 초기화
#         self.model, self.tokenizer = load_model_and_tokenizer()
    
        
#         # RAG 초기화
#         asyncio.run(self.initialize_rag_async())

#         print("모델, 토크나이저, RAG가 서버 시작 시 초기화되었습니다.")


#     async def initialize_rag_async(self):
#         await initialize_rag()

