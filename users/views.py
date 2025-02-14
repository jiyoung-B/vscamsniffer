from django.contrib.auth import logout
from django.http import JsonResponse
from allauth.socialaccount.models import SocialAccount
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse, HttpResponseRedirect
from allauth.socialaccount.models import SocialAccount
from .models import UserInputData
from django.views import View
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# ✅ 사용자 목록 반환
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 인증된 사용자만 접근 가능
def user_list(request):
    users = list(User.objects.values("id", "username", "email"))
    return JsonResponse(users, safe=False)

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


# ✅ 로그아웃 처리
@api_view(['POST'])
def user_logout(request):
    """로그아웃 처리 및 세션 제거"""
    logout(request)
    return JsonResponse({"message": "Logout successful"}, status=200)


# ✅ 보호된 뷰 (테스트용)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """JWT 인증이 필요한 보호된 뷰"""
    return JsonResponse({"message": f"Hello, {request.user.username}! This is a protected view."}, status=200)


@api_view(['GET'])
def google_login_callback(request):
    """Google 소셜 로그인 후 JWT 토큰 반환"""
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"error": "Authentication failed"}, status=401)
        
        # ✅ JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        token_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        # ✅ React로 리디렉트하며 토큰 전달 (프론트엔드에서 저장)
        response = HttpResponseRedirect("http://localhost:3000/")
        response.set_cookie("accessToken", token_data["access"], httponly=False)
        response.set_cookie("refreshToken", token_data["refresh"], httponly=False)
        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


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
