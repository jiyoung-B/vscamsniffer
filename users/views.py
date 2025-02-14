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

# users/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def get_user_info(request):
    user = request.user
    user_info = {
        "username": user.username,
        "email": user.email,
    }
    return JsonResponse(user_info)


# # ✅ JWT 기반 사용자 정보 반환
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_user_info(request):
#     """현재 로그인된 사용자 정보 반환 (JWT 인증)"""
#     user_info = {
#         "username": request.user.username,
#         "email": request.user.email,
#     }
#     try:
#         social_account = SocialAccount.objects.get(user=request.user)
#         user_info["provider"] = social_account.provider
#         user_info["social_id"] = social_account.uid
#     except SocialAccount.DoesNotExist:
#         user_info["provider"] = "local"

#     return JsonResponse(user_info, status=200)





logger = logging.getLogger(__name__)


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
