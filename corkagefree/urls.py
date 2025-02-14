from django.contrib import admin
from django.urls import path, include
from users.views import DataListView, AddDataView
from django.urls import path
from django.conf.urls import include
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.generic import TemplateView  # React 파일을 서빙하기 위해 사용
from users.views import google_login,google_callback
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

class GoogleLogin(SocialLoginView):  
    adapter_class = GoogleOAuth2Adapter  # Google OAuth2 어댑터 지정





urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('users.urls')),  # 기존 allauth 경로
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("api/auth/google/", GoogleLogin.as_view(), name="google_login"),
    path('', TemplateView.as_view(template_name="index.html"), name='home'),
    path("api/data-list/", DataListView.as_view(), name="data_list"),
    path("api/add-data/", AddDataView.as_view(), name="add_data"),
    path('rollplaying/', include('rp.urls')),
]


#미디어 파일 저장
from django.conf.urls.static import static
from django.conf import settings

# MEDIA_URL로 들어오는 요청에 대해 MEDIA_ROOT 경로를 탐색한다.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
