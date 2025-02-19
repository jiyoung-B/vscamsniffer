from functools import lru_cache
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from transformers import BitsAndBytesConfig

# 전역 변수 설정
loaded_model = None

@lru_cache(maxsize=1)
def load_model_and_tokenizer():
    global loaded_model
    
    # 이미 모델이 로드된 경우 캐시된 모델 반환
    if loaded_model is not None:
        print("모델이 이미 로드되어 있습니다.")
        return loaded_model
    
    print("모델 초기화 시작...")
    # 4비트 양자화 설정
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
    )

    # 토크나이저 로드
    tokenizer = AutoTokenizer.from_pretrained(
        "MLP-KTLim/llama-3-Korean-Bllossom-8B",
        use_fast=True,
        model_max_length=2048,
        padding_side="left"
    )
    print("토크나이저 로드 완료")

    # 모델 로드
    base_model = AutoModelForCausalLM.from_pretrained(
        "MLP-KTLim/llama-3-Korean-Bllossom-8B",
        quantization_config=bnb_config,
        torch_dtype=torch.float16,
        device_map="cuda",
        low_cpu_mem_usage=True,
        offload_folder="offload",
    )
    print("기본 모델 로드 완료")

    # LoRA 어댑터 로드
    adapter_path = "/home/azureuser/Desktop/BE"
    model = PeftModel.from_pretrained(
        base_model,
        adapter_path,
        torch_dtype=torch.float16,
    )
    print("LoRA 어댑터 로드 완료")

    model.eval()
    
    # 전역 변수 저장
    loaded_model = (model, tokenizer)
    return loaded_model
