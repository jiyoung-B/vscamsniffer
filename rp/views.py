from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View




def rollplaying(request,user_id=None):
    user = get_object_or_404(User, id=user_id)
    if request.user.is_authenticated and request.user.id == user.id:
        user_id = request.user.id
        return render(request,"RP.html",{"user_id":user_id})
    else:
        return HttpResponse("페이지에 대한 접근 권한이 없습니다.")
    
#특정 view에 대해 CSRF 보호를 비활성화
class GetChatbotAnswerView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("chatbot function called")
        data = json.loads(request.body)
        query = data.get('query')
        # ans = get_answer(query)
        response_data = {'answer': data}

        response = JsonResponse(response_data)
        response["Access-Control-Allow-Origin"] = "*"  # 모든 출처 허용
        response["Access-Control-Allow-Methods"] = "POST"  # 허용할 메서드 설정

        return response

    # def get_answer(question):
    #     query = question
    #     current_dir = os.path.dirname(os.path.abspath(__file__))
    #     data_file_path = os.path.join(current_dir, 'data.txt')
    #     loader = TextLoader(data_file_path)
    #     index = VectorstoreIndexCreator().from_loaders([loader])
    #     ans = index.query(query)

    #     return ans

