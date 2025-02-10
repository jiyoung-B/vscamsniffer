from django.urls import path
from .views import upload_audio
from django.http import HttpResponse

def index(request):
    return HttpResponse("Attach 메인 페이지입니다.")

urlpatterns = [
    path('', index, name='attach_index'),  # 기본 경로 추가
    path('upload/', upload_audio, name='upload_audio'),
]
