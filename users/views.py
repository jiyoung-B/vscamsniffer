from django.contrib.auth import logout
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse, HttpResponseRedirect
from allauth.socialaccount.models import SocialAccount
from .models import *
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from rest_framework import status
from django.views import View
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from django.shortcuts import redirect
#login test
import logging
import dotenv


# 구글 소셜로그인 변수 설정
dotenv.load_dotenv()

state = os.environ.get("STATE")
BASE_URL = 'http://127.0.0.1:8000/'
GOOGLE_CALLBACK_URI = 'http://127.0.0.1:8000/accounts/google/callback/'



# 구글 로그인
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")




logger = logging.getLogger(__name__)

def google_callback(request):
    return request

# def GoogleLogin(request):
#     return request



# 데이터 목록 반환
class DataListView(View):
    def get(self, request):
        data = list(UserInputData.objects.values("id", "content"))
        return JsonResponse(data, safe=False)

# 입력 데이터 저장
@method_decorator(csrf_exempt, name='dispatch')
class AddDataView(View):
    def post(self, request):
        try:
            body = json.loads(request.body.decode("utf-8"))  # ✅ 문자열을 UTF-8로 디코딩
            content = body.get("content", "")
            if content:
                UserInputData.objects.create(content=content)
                return JsonResponse({"message": "성공적으로 저장되었습니다."}, status=201)
            return JsonResponse({"error": "빈 입력값입니다."}, status=400)
        except json.JSONDecodeError:  # ✅ JSON 파싱 에러 처리
            return JsonResponse({"error": "유효하지 않은 JSON 형식입니다."}, status=400)
        except Exception as e:  # ✅ 기타 에러 처리
            return JsonResponse({"error": str(e)}, status=500)
