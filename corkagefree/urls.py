from django.contrib import admin
from django.urls import path, include
from users.views import get_user_info, user_logout, user_list, protected_view, DataListView, AddDataView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.generic import TemplateView
from users.views import google_login_callback

urlpatterns = [
    # 기존 관리자 및 소셜 로그인
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/google/login/callback/', google_login_callback, name='google_callback'),

    # 사용자 API
    path('api/user/', get_user_info, name='get_user_info'),
    path('api/logout/', user_logout, name='user_logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # React 앱 서빙
    path('', TemplateView.as_view(template_name="index.html"), name='home'),

    # 데이터 관리 API
    path("api/data-list/", DataListView.as_view(), name="data_list"),
    path("api/add-data/", AddDataView.as_view(), name="add_data"),

    # 롤플레잉 기능 (기존 유지)
    path('rollplaying/', include('rp.urls')),

    # 새로 추가된 음성 파일 업로드 기능
    path('attach/', include('attach.urls')),
]
