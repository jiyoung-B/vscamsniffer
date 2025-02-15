from django.contrib import admin
from django.urls import path, include
from users.views import get_user_info, user_logout, protected_view, DataListView, AddDataView, naver_login_callback

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView  # React 파일을 서빙하기 위해 사용
# from users.views import google_login_callback

from django.conf import settings
from django.conf.urls.static import static

from attach.views import AudioFileUploadView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/user/', get_user_info, name='get_user_info'),
    path('api/logout/', user_logout, name='user_logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('accounts/google/login/callback/', google_login_callback, name='google_callback'),  # ✅ 추가된 경로
    path('accounts/naver/login/callback/', naver_login_callback, name='naver_callback'),  # ✅ 네이버 로그인 콜백
    path('', TemplateView.as_view(template_name="index.html"), name='home'),
    path("api/data-list/", DataListView.as_view(), name="data_list"),
    path("api/add-data/", AddDataView.as_view(), name="add_data"),
    
    path("upload-audio/", AudioFileUploadView.as_view(), name="audio-upload"),
    path("attach/", include("attach.urls")),
]
