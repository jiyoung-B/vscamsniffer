from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.settings import Settings
import asyncio


async def initialize_rag():
    from rp.consumers import RPConsumer
    #RAG 초기화 (재호출 방지)
    if RPConsumer.scenario_index and RPConsumer.strategy_index:
        return RPConsumer.scenario_index, RPConsumer.strategy_index
    try:
        scenario_data = await asyncio.to_thread(SimpleDirectoryReader("rag").load_data)
        strategy_data = await asyncio.to_thread(SimpleDirectoryReader("rag2").load_data)

        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", use_auth_token=False)
        
        RPConsumer.scenario_index = await asyncio.to_thread(VectorStoreIndex.from_documents, scenario_data, embed_model=embed_model)
        RPConsumer.strategy_index = await asyncio.to_thread(VectorStoreIndex.from_documents, strategy_data, embed_model=embed_model)

        return RPConsumer.scenario_index, RPConsumer.strategy_index

    except Exception as e:
        print(f"RAG 초기화 중 오류 발생: {e}")
        return None, None

async def get_scenario_content(self):
        try:
            scenario_index = self.scenario_index or RPConsumer.scenario_index
            print("보이스피싱 시나리오 콘텐츠 조회중......")
            if not self.scenario_index:
                raise ValueError("시나리오 인덱스 - 초기화 실패")
                
            scenario_engine = self.scenario_index.as_query_engine()
            response = await asyncio.to_thread(
                scenario_engine.query,
                "보이스피싱 시뮬레이션에 사용할 내용을 제공해줘."
            )
            
            if not response or not response.response:
                raise ValueError("시나리오 콘텐츠를 가져오기 실패")
                
            return response.response
        except Exception as e:
            print(f"시나리오 콘텐츠 조회 오류: {e}")
            raise

    # 대응 전략 콘텐츠 조회
async def get_strategy_content(self):
        try:
            strategy_index = self.strategy_index or RPConsumer.strategy_index
            print("보이스피싱 대응 전략 콘텐츠를 조회중.....")
            if not self.strategy_index:
                raise ValueError("전략 인덱스가 초기화되지 않았습니다")
                
            strategy_engine = self.strategy_index.as_query_engine()
            print("보이스피싱 대응 엔진이 완료되었습니다! 쿼리 생성중...")
            response = await asyncio.to_thread(
                strategy_engine.query,
                "보이스피싱 대응 전략을 제공해줘."
            )
            
            if not response or not response.response:
                raise ValueError("전략 콘텐츠를 가져오지 못했습니다")
                
            return response.response
        except Exception as e:
            print(f"전략 콘텐츠 조회 오류: {e}")
            raise
