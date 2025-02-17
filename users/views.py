from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from allauth.socialaccount.models import SocialAccount
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views import View
from django.conf import settings
from .models import UserInputData
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

# ✅ Preflight 요청 핸들링 함수
def handle_options_request(request):
    response = HttpResponse(status=200)
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Cache-Control, Pragma"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Max-Age"] = "86400"
    return response

# ✅ 사용자 정보 반환 뷰 (CORS Preflight 처리 포함)
@csrf_exempt
@api_view(["GET", "OPTIONS"])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    if request.method == "OPTIONS":
        return handle_options_request(request)

    user_info = {
        "username": request.user.username,
        "email": request.user.email,
    }
    return JsonResponse(user_info, status=200)


# ✅ Google 로그인 후 JWT 토큰 반환 및 리디렉트
@api_view(["GET"])
def google_login_callback(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"error": "Authentication failed"}, status=401)

        refresh = RefreshToken.for_user(user)
        token_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        redirect_url = f"{settings.LOGIN_REDIRECT_URL}?accessToken={token_data['access']}&refreshToken={token_data['refresh']}"
        response = HttpResponseRedirect(redirect_url)
        response.set_cookie("accessToken", token_data["access"], httponly=False)
        response.set_cookie("refreshToken", token_data["refresh"], httponly=False)
        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ✅ 로그아웃 처리
@api_view(['POST'])
def user_logout(request):
    logout(request)
    return JsonResponse({"message": "Logout successful"}, status=200)

# ✅ 보호된 뷰 (테스트용)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return JsonResponse({"message": f"Hello, {request.user.username}! This is a protected view."}, status=200)

# ✅ 데이터 목록 반환
class DataListView(View):
    def get(self, request):
        data = list(UserInputData.objects.values("id", "content"))
        return JsonResponse(data, safe=False)

# ✅ 입력 데이터 저장
@method_decorator(csrf_exempt, name='dispatch')
class AddDataView(View):
    def post(self, request):
        try:
            body = json.loads(request.body.decode("utf-8"))
            content = body.get("content", "")
            if content:
                UserInputData.objects.create(content=content)
                return JsonResponse({"message": "성공적으로 저장되었습니다."}, status=201)
            return JsonResponse({"error": "빈 입력값입니다."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "유효하지 않은 JSON 형식입니다."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# ✅ 네이버 소셜 로그인 후 JWT 토큰 반환 및 리디렉트
@api_view(['GET'])
def naver_login_callback(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"error": "Authentication failed"}, status=401)

        refresh = RefreshToken.for_user(user)
        token_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        response = HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        response.set_cookie("accessToken", token_data["access"], httponly=False)
        response.set_cookie("refreshToken", token_data["refresh"], httponly=False)
        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
