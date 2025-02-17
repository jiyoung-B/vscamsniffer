# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.http import HttpResponseRedirect
# from django.conf import settings
# from allauth.exceptions import ImmediateHttpResponse  # ✅ 추가 필요


# class MySocialAccountAdapter(DefaultSocialAccountAdapter):
#     def pre_social_login(self, request, sociallogin):
#         """로그인 직전 호출되는 메서드"""
#         print("🔵 pre_social_login 호출됨")

#         if not sociallogin.is_existing:
#             print("🔴 신규 사용자입니다. 사용자 정보를 저장합니다.")
#             user = sociallogin.user
#             user.set_unusable_password()  # 소셜 로그인 사용자는 비밀번호가 필요 없음
#             user.save()
#             print(f"✅ 사용자 저장 완료: {user}")

#         # ✅ JWT 토큰 생성
#         user = sociallogin.user
#         refresh = RefreshToken.for_user(user)
#         token_data = {
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#         }

#         print("✅ 토큰 생성 완료:", token_data)

#         # ✅ React로 리디렉션하며 URL에 토큰 추가
#         redirect_url = f"{settings.LOGIN_REDIRECT_URL}?accessToken={token_data['access']}&refreshToken={token_data['refresh']}"
#         print("🔄 리디렉트 URL:", redirect_url)

#         # ✅ 즉시 리디렉션 반환 (흐름 종료)
#         raise ImmediateHttpResponse(HttpResponseRedirect(redirect_url))

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
from django.conf import settings
from allauth.exceptions import ImmediateHttpResponse
from django.contrib.auth.models import User

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """소셜 로그인 직전 호출되는 메서드"""
        print("🔵 pre_social_login 호출됨")

        user = sociallogin.user
        if not user.id:  # 새로운 사용자일 때만 처리
            if User.objects.filter(email=user.email).exists():
                print("⚠️ 이메일 중복 사용자입니다. 기존 사용자와 연결합니다.")
                existing_user = User.objects.get(email=user.email)
                sociallogin.connect(request, existing_user)
            else:
                print("🔴 신규 사용자입니다. 사용자 정보를 저장합니다.")
                user.set_unusable_password()  # 비밀번호는 사용하지 않음
                user.save()

        # ✅ JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        token_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        print("✅ 토큰 생성 완료:", token_data)

        # ✅ React로 리디렉션하며 URL에 토큰 추가
        redirect_url = f"{settings.LOGIN_REDIRECT_URL}?accessToken={token_data['access']}&refreshToken={token_data['refresh']}"
        print("🔄 리디렉트 URL:", redirect_url)

        # ✅ 흐름 종료 후 리디렉션
        raise ImmediateHttpResponse(HttpResponseRedirect(redirect_url))
