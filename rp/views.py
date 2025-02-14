from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests






def text_to_speech(text):
    api_key = "sk_4d122a369f86cf7295e346b1f28b47da2e4ab2d6bcc9d9bc"
    url = "https://api.elevenlabs.io/v1/text-to-speech/generate"
    
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # 예시 voice_id와 텍스트
    voice_id = "PLfpgtLkFW07fDYbUiRJ"
    
    data = {
        "voice_id": voice_id,
        "text": text,
        "output_format": "mp3"  # mp3 형식으로 음성 생성
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        # 음성 파일의 URL을 반환 (실제 웹소켓에서 음성을 전송하려면 base64로 인코딩하거나 파일 경로로 처리 가능)
        return response.content  # 응답으로 받은 음성을 직접 반환
    else:
        return None  # 오류가 발생한 경우



# 특정 view에 대해 CSRF 보호를 비활성화
class GetChatbotAnswerView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("chatbot function called")
        data = json.loads(request.body)
        query = data.get('query')
        # ans = get_answer(query)  # 이곳에 실제 챗봇 응답 처리 로직을 추가
        
        response_data = {'answer': query}  # 이곳은 임시 응답입니다.
        
        # 음성을 TTS로 변환
        audio_url = text_to_speech(response_data['answer'])

        if audio_url:
            response = {
                'answer': response_data,
                'audio_url': f"/midia/{audio_url}"  # 음성 파일의 경로 반환
            }
        else:
            response = {
                'answer': response_data,
                'audio_url': None  # 음성 변환 실패
            }

        return JsonResponse(response)



def rollplaying(request,user_id=None):
    user = get_object_or_404(User, id=user_id)
    if request.user.is_authenticated and request.user.id == user.id:
        user_id = request.user.id
        return render(request,"RP.html",{"user_id":user_id})
    else:
        return HttpResponse("페이지에 대한 접근 권한이 없습니다.")


    # def get_answer(question):
    #     query = question
    #     current_dir = os.path.dirname(os.path.abspath(__file__))
    #     data_file_path = os.path.join(current_dir, 'data.txt')
    #     loader = TextLoader(data_file_path)
    #     index = VectorstoreIndexCreator().from_loaders([loader])
    #     ans = index.query(query)

    #     return ans

